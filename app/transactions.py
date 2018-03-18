
"""
Structures for the Bitcoin transactions network and Bitcoin addresses
"""

import sys

from .bitcoin import Transaction, TransactionInput, TransactionOutput
from .users import UserNetwork


class TransactionNetwork:
    """
    List of transactions with an unique set of all encountered addresses
    (as inputs or outputs of all transactions)
    """
    def __init__(self):
        self.addresses = UserNetwork()

    def build(self, spark_df):
        """ From a Spark dataframe following the json format build the transaction network

        :param spark_df: PySpark Dataframe object of bitcoin transactions
        """

        ite = spark_df.toLocalIterator()

        transactions_count = 0
        for t in ite:
            self.addresses.add_transaction(TransactionNetwork.json_to_transaction(t))

            transactions_count += 1
            sys.stdout.write("\r{} transactions".format(transactions_count))
            sys.stdout.flush()

        # print(self.addresses)
        self.addresses.close()
        print(self.addresses.heuristics_used)

    @staticmethod
    def json_to_transaction(transaction_json):
        """ Create Transaction object from json representation

        :param transaction_json: JSON Object of a transaction
        """
        transaction_inputs = []
        transaction_outputs = []

        for t_in in transaction_json.tx_ins:
            transaction_in = TransactionInput(t_in.address, t_in.value)
            transaction_inputs.append(transaction_in)

        for t_out in transaction_json.tx_outs:
            transaction_out = TransactionOutput(t_out.address, t_out.value)
            transaction_outputs.append(transaction_out)

        return Transaction(transaction_inputs, transaction_outputs, transaction_json.timestamp)
