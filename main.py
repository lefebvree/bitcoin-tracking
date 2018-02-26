
"""
Initialise PySpark and create the Transactions network
from json data files (specified in databaseconfig.py)
"""

from pyspark.sql import SparkSession

from os import path

from app.network import TransactionNetwork
from app.databaseconfig import pyspark as cfg


def main():

    spark = SparkSession.builder \
        .master("local") \
        .appName("Bitcoin Tracking") \
        .config("spark.executor.memory", cfg['memory']) \
        .getOrCreate()

    transactions_dataframe = spark.read.json(path.join("hdfs://", cfg['hdfs_path']))

    transactions_network = TransactionNetwork()
    transactions_network.build(transactions_dataframe)


if __name__ == '__main__':
    main()
