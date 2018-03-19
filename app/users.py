
"""
Methods and heuristics used to build the bitcoin user network graph from transactions list
"""

from .graph_database_driver import GraphDatabaseDriver


class UserNetwork:
    """ Process transactions and populate the GraphDatabaseDriver with addresses and their relations

    """
    def __init__(self):
        self.driver = GraphDatabaseDriver()
        # Keep track of each heuristic usage
        self.heuristics_used = [0, 0, 0, 0]

    def close(self):
        self.driver.close()

    def add_transaction(self, transaction):
        """ Process a bitcoin transaction and addresses and relations to the graph database

        """
        clause = self.driver.create_transaction_clause()

        for a in transaction.inputs + transaction.outputs:
            clause.add_address(a.address)

        # Applies heuristics

        if len(transaction.inputs) > 1:
            self.h1_inputs(transaction, clause)

        if len(transaction.outputs) == 2:
            self.h2_change_address(transaction, clause)

        clause.execute()

    def h1_inputs(self, transaction, clause):
        """ All addresses used as input of the same transaction belong to the
        same controlling entity, called a User.
        """
        # For every combination of input addresses an edge is added to the graph
        for input_transaction in transaction.inputs[1:]:
            clause.add_edge_between(transaction.inputs[0].address, input_transaction.address)

        self.heuristics_used[0] += 1

    def h2_change_address(self, transaction, clause):
        """ If there are exactly two output-addresses a1 and a2, that one of them
        (a1) appears for the first time and that the other (a2) has appeared before, then a1
        is considered to be the change address.
        """
        a1_known_address = self.driver.address_exists(transaction.outputs[0].address)
        a2_known_address = self.driver.address_exists(transaction.outputs[1].address)

        change_address = None

        # a1 is the change address
        if a2_known_address and not a1_known_address:
            change_address = transaction.outputs[0].address
        # a2 is the change address
        elif a1_known_address and not a2_known_address:
            change_address = transaction.outputs[1].address

        if change_address is not None:
            for input_transaction in transaction.inputs:
                clause.add_edge_between(input_transaction.address, change_address)

            self.heuristics_used[1] += 1
