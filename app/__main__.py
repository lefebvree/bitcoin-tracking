
"""

"""

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

from os import path

import databaseconfig as cfg


def main():

    spark = SparkSession.builder \
        .master("local") \
        .appName("Bitcoin Tracking") \
        .config("spark.executor.memory", cfg.pyspark['memory']) \
        .getOrCreate()

    df = spark.read.json(path.join("hdfs://", cfg.pyspark['hdfs_path']))
    print(df.count())


if __name__ == '__main__':
    main()
