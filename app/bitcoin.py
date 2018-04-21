
"""
Structures representing Bitcoin transactions

Each transaction consist of m inputs and n outputs each associated with
a public key representing a bitcoin address and a bitcoin amount
"""


class Transaction:
    """ Single bitcoin transaction recording an exchange from a
        list of inputs to a list of outputs

    :param inputs: List of TransactionInput
    :param outputs: List of TransactionOutput
    :param timestamp: Int value of approximate transaction timestamp
    """
    def __init__(self, inputs, outputs, timestamp):
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = timestamp


class TransactionInput:
    """ Input of a bitcoin transaction associating a Bitcoin address with a bitcoin value

    :param address: String of bitcoin address public key
    :param value:  Float bitcoin value
    """
    def __init__(self, address, value):
        self.address = address
        self.value = value


class TransactionOutput:
    """ Output of a bitcoin transaction associating a Bitcoin address with a bitcoin value

    :param address: String of bitcoin address public key
    :param value:  Float bitcoin value
    """
    def __init__(self, address, value):
        self.address = address
        self.value = value
