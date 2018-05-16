
"""
Initialise PySpark and create the Transactions network
from json data files (specified in databaseconfig.py)
"""

from pyspark.sql import SparkSession

from os import path

from app.transactions import TransactionNetwork
from app.databaseconfig import pyspark as cfg


def main():

    print("Initialising PySpark executor...")
    spark = SparkSession.builder \
        .master("local") \
        .appName("Bitcoin Tracking") \
        .config("spark.executor.memory", cfg['memory']) \
        .getOrCreate()

    transactions_dataframe = spark.read.json(path.join("hdfs://", cfg['hdfs_path']))

    print("Initialising Neo4j session...")
    transactions_network = TransactionNetwork()
    transactions_network.build(transactions_dataframe)

    transactions_network.addresses.generate_users_nodes()

    transactions_network.build_identity_hint_network(transactions_dataframe)
    transactions_network.addresses.community_detection()


if __name__ == '__main__':
    main()
