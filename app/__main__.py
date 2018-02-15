
"""

"""

from pyspark import SparkConf, SparkContext


def main():
    conf = (SparkConf()
            .setMaster("local")
            .setAppName("Bitcoin Tracking")
            .set("spark.executor.memory", "1g"))
    sc = SparkContext(conf=conf)


if __name__ == '__main__':
    main()
