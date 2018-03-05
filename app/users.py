
"""
Heuristics used to identify users
"""


import networkx as nx

from itertools import combinations


class UserNetwork:

    def __init__(self):
        self.addresses = nx.Graph()

    def __str__(self):
        return ' '.join([str(len(self.addresses)), "addresses -",
                         str(len(list(nx.connected_components(self.addresses)))), "users"])

    def update_with_transaction(self, transaction):
        """

        :param transaction:
        :return:
        """
        if len(transaction.inputs) > 1:
            self.h1_inputs(transaction)

        if len(transaction.outputs) == 2:
            self.h2_change_address(transaction)

        # Add addresses not added with heuristics
        for address in transaction.inputs + transaction.outputs:
            self.addresses.add_node(address)

    def h1_inputs(self, transaction):
        """
        All addresses used as input of the same transaction belong to the
        same controlling entity, called a User.
        """
        # For every combination of input addresses an edge is added to the graph
        self.addresses.add_edges_from(combinations(transaction.inputs, 2))

    def h2_change_address(self, transaction):
        """
        If there are exactly two output-addresses a1 and a2, that one of them
        (a1) appears for the first time and that the other (a2) has appeared before, then a1
        is considered to be the change address.
        """
        a1_known_address = transaction.outputs[0] in self.addresses
        a2_known_address = transaction.outputs[1] in self.addresses

        change_address = None

        # a1 is the change address
        if a2_known_address and not a1_known_address:
            change_address = transaction.outputs[0]
        # a2 is the change address
        elif a1_known_address and not a2_known_address:
            change_address = transaction.outputs[1]

        if change_address is not None:
            for input_address in transaction.inputs:
                self.addresses.add_edge(input_address, change_address)

