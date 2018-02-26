
"""
Structures for the Bitcoin transactions network and Bitcoin addresses
"""


from .bitcoin import Transaction, Address, TransactionInput, TransactionOutput


class TransactionNetwork:
    """
    List of transactions with an unique set of all encountered addresses
    (as inputs or outputs of all transactions)
    """
    def __init__(self):
        self.transactions = []
        self.addresses = set()

    def build(self, spark_df):
        """ From a Spark dataframe following the json format build the transaction network

        :param spark_df: PySpark Dataframe object of bitcoin transactions
        """
        spark_df.foreach(self.add_transaction_from_json)

        print(len(self.transactions), "transactions loaded")
        print(len(self.addresses), "addresses loaded")

    def add_transaction_from_json(self, transaction_json):
        """ Create Transaction object from json representation

        :param transaction_json: JSON Object of a transaction
        """
        transaction_inputs = []
        transaction_outputs = []

        for t_in in transaction_json.tx_ins:
            address = Address(t_in.address)
            self.addresses.add(address)

            transaction_in = TransactionInput(address, t_in.value)
            transaction_inputs.append(transaction_in)

        for t_out in transaction_json.tx_outs:
            address = Address(t_out.address)
            self.addresses.add(address)

            transaction_out = TransactionOutput(address, t_out.value)
            transaction_outputs.append(transaction_out)

        transaction = Transaction(transaction_inputs, transaction_outputs, transaction_json.timestamp)
        self.transactions.append(transaction)
