
"""
Methods and heuristics used to build the bitcoin user network graph from transactions list
"""

from .graph_database_driver import GraphDatabaseDriver


class UserNetwork:
    """ Process transactions and populate the GraphDatabaseDriver with addresses and their relations

    """
    def __init__(self):
        self.driver = GraphDatabaseDriver()

        self.heuristics_enabled = [self.h1_inputs]
        # Keep track of each heuristic usage
        self.heuristics_used = [0, 0, 0, 0]

        # Keep set of known addresses (input or output)
        self.known_addresses = set()

        # Dictionary of all addresses after H1 with user id
        self.known_users = dict()

    def close(self):
        self.driver.close()

    def populate_known_addresses(self):
        """ Fetch addresses from graph database and add addresses to known addresses set

        """
        address_count = self.driver.get_address_count()

        if address_count > 0:
            print("Fetching", address_count, "addresses from database")
            self.driver.fetch_all_known_addresses(self.add_known_address)
            print(len(self.known_addresses), "uniques addresses added\n")

        else:
            print("No already known addresses in database")

    def populate_known_addresses_with_users(self):
        print("Fetching all addresses with users from database")
        self.driver.fetch_all_known_addresses_with_users(self.add_known_address_with_user)
        print(len(self.known_users), "uniques addresses with users added\n")

    def commit_new_entries(self):
        self.driver.commit_additions()

    def commit_new_user_relations(self):
        self.driver.commit_user_relations()

    def add_transaction(self, transaction):
        """ Process a bitcoin transaction and addresses and relations to the graph database

        """
        # Applies enabled heuristics
        for heuristic in self.heuristics_enabled:
            heuristic(transaction)

        for a in transaction.inputs + transaction.outputs:
            if not self.is_known_address(a.address):
                self.add_known_address(a.address)
                self.driver.add_address(a.address)

    def add_known_address(self, address):
        """ Add an address to known addresses list after converting it to byte array

        :param address: String of bitcoin address
        """
        b58_address = self.encode_address(address)
        self.known_addresses.add(b58_address)

    def is_known_address(self, address):
        """ Check if address is in known addresses set

        :param address: String of bitcoin address
        """
        return self.encode_address(address) in self.known_addresses

    def add_known_address_with_user(self, address, user):
        """ Add a key from given address to known_users returning user's is

        :param address: String of bitcoin address
        :param user: Id of owner
        """
        b58_address = self.encode_address(address)
        self.known_users[b58_address] = int(user)

    def get_user_id_from_address(self, address):
        """ Return id o user associated with address

        :param address: String of bitcoin address
        :return: Id of user
        """
        b58_address = self.encode_address(address)
        if b58_address in self.known_users:
            return self.known_users[b58_address]
        else:
            return None

    def generate_users_nodes(self):
        print("Finding connected components from addresses...")
        user_count = self.driver.find_connected_components()

        print(user_count, "unique users found, creating User nodes...")
        self.driver.create_user_nodes()

        print("User nodes created\n")

    @staticmethod
    def encode_address(address):
        """ Convert address string to byte array

        :param address: String of bitcoin address
        """
        return str.encode(address)

    def h1_inputs(self, transaction):
        """ All addresses used as input of the same transaction belong to the
            same controlling entity, called a User.
        """
        # If more than 1 input address
        if len(transaction.inputs) > 1:
            # An edge is added between the first input address and all the others
            for input_transaction in transaction.inputs[1:]:
                self.driver.add_relation([transaction.inputs[0].address, input_transaction.address])

            self.heuristics_used[0] += 1

    def h2_change_address(self, transaction):
        """ If there are exactly two output-addresses a1 and a2, that one of them
            (a1) appears for the first time and that the other (a2) has appeared before, then a1
            is considered to be the change address.
        """
        # 2 output addresses exactly
        if len(transaction.outputs) == 2:
            a1_known_address = self.is_known_address(transaction.outputs[0].address)
            a2_known_address = self.is_known_address(transaction.outputs[1].address)

            change_address = None

            # a1 is the change address
            if a2_known_address and not a1_known_address:
                change_address = transaction.outputs[0].address
            # a2 is the change address
            elif a1_known_address and not a2_known_address:
                change_address = transaction.outputs[1].address

            if change_address is not None:
                for input_transaction in transaction.inputs:
                    self.driver.add_relation([input_transaction.address, change_address])

                self.heuristics_used[1] += 1

    def h3_one_time_change_address(self, transaction):
        """ An address is considered a one-time change address if it satisfies the following properties:
            - The transaction is not a coin generation
            - The address is not among the input addresses (address reuse)
            - It is the only output address appearing for the first time
        """
        # Coinbase transaction (coin generation) have address hash "0" as input
        if transaction.inputs[0].address != "0":

            first_time_address = False
            one_time_change_address = None

            for output_address in transaction.outputs:

                # Check if it is the only one to appear for the first time
                if not self.is_known_address(output_address.address):
                    if first_time_address:
                        # At least two new addresses as outputs
                        return
                    else:
                        first_time_address = True

                    # Check if not among inputs
                    if output_address.address not in map(lambda a: a.address, transaction.inputs):
                        one_time_change_address = output_address.address

            if one_time_change_address is not None:
                for input_transaction in transaction.inputs:
                    self.driver.add_relation([input_transaction.address, one_time_change_address])

                self.heuristics_used[2] += 1

    def h4_community_detection(self, transaction):
        """ 1. A first level of aggregation is created by applying H1. Sets of addresses belonging
               to a same user are used as nodes of the hint network
            2. For each transaction in the dataset, considering users found by H1 instead of
               individual addresses, an edge is added (if not already present) between the (necessarily
               unique) sender and each recipient if:
               • there are less than 10 users in the ouput of the transaction (recipients)
               • all recipients are different from the sender, i.e there is no already known
               change address

            On this network, a community detection algorithm is applied. Communities correspond
            to unique users
        """
        if len(transaction.outputs) < 10:
            # Get the user id from known_users
            sender_id = self.get_user_id_from_address(transaction.inputs[0].address)
            if sender_id is None:
                return

            for output in transaction.outputs:
                # A recipient is the same as the sender
                recipient = self.get_user_id_from_address(output.address)
                if recipient is None or recipient == sender_id:
                    return

            for output in transaction.outputs:
                recipient_id = self.get_user_id_from_address(output.address)
                value = int(output.value)
                self.driver.add_user_relation(sender_id, recipient_id, value)

    def community_detection(self):
        """ Apply a community detection algorithm to uniques users nodes with transactions as edges

        """
        self.driver.run_louvain_algorithm()
