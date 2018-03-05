
"""
Heuristics used to identify users
"""

from itertools import combinations


def h1_reidentification_from_inputs(addresses_graph, transaction_inputs):
    """
    All addresses used as input of the same transaction belong to the
    same controlling entity, called a User.
    """
    if len(transaction_inputs) > 1:
        # For every combination of input addresses an edge is added to the graph
        addresses_graph.add_edges_from(combinations(transaction_inputs, 2))

