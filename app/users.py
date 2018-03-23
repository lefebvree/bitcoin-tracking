
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

    def close(self):
        self.driver.close()

    def commit_new_entries(self):
        self.driver.commit_additions()

    def add_transaction(self, transaction):
        """ Process a bitcoin transaction and addresses and relations to the graph database

        """
        for a in transaction.inputs + transaction.outputs:
            if a.address not in self.known_addresses:
                self.known_addresses.add(a.address)
                self.driver.add_address(a.address)

        # Applies enabled heuristics
        for heuristic in self.heuristics_enabled:
            heuristic(transaction)

        # clause.execute()

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
            # a1_known_address = self.driver.address_exists(transaction.outputs[0].address)
            # a2_known_address = self.driver.address_exists(transaction.outputs[1].address)
            a1_known_address = transaction.outputs[0].address in self.known_addresses
            a2_known_address = transaction.outputs[1].address in self.known_addresses

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
                if output_address.address not in self.known_addresses:
                    if first_time_address:
                        # At least two new addresses as outputs
                        return
                    else:
                        first_time_address = True

                    # Check if not among inputs
                    if output_address.address not in map(lambda a: a.address, transaction.inputs):
                        one_time_change_address = output_address

            if one_time_change_address is not None:
                for input_transaction in transaction.inputs:
                    self.driver.add_relation([input_transaction.address, one_time_change_address])

                self.heuristics_used[2] += 1

