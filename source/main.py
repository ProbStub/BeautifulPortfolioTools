import os
from dotenv import load_dotenv

import pyspark
from pyspark.sql import SparkSession

def run():
    """
    Program initiation function parsing user parameters, providing help and launching the application

    Returns:
        -

    """
    # TODO: Add user parameter parsing and basic help output

    print("Initiating...")
    load_dotenv()
    mongo_host = os.getenv("MONGO_HOST")
    mongo_user = os.getenv("MONGO_USER")
    mongo_pwd = os.getenv("MONGO_PWD")


    spark = __start_mongo_spark__(mongo_host, mongo_user, mongo_pwd)

    print("...closing down")

def __start_plain_spark__():
    """
        Initiates and configures spark session parameters:
            - Enabling arrow for efficient pandas <-> spark dataframe conversion
            - No executor CPU/memory ask to allow cluster auto-scale optimization

        Args:
            -
        Returns:
            Configured SparkSession
        Raises:
            -
        """
    spark = SparkSession.builder.appName("BPT-App-Std") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .getOrCreate()

    return spark

def __start_mongo_spark__(mongo_host, mongo_user, mongo_pwd):
    if mongo_user is None or mongo_pwd is None:
        raise RuntimeError("Cannot start MongoDB connection due to missing login credentials.")
    else:
        # Note: MongoDB Atlas -> mongodb+srv and no ports! Using mongo-spark connector 3.0.1
        # verify package JARs download to cluster nodes -> check logs for :: resolving dependencies ::
        # Also DB=sample_analytics, Collection=Customers
        conf = pyspark.SparkConf()
        conf.set("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1")
        conf.set("spark.mongodb.input.uri", "mongodb+srv://" \
                 + mongo_user + ":" + mongo_pwd + "@" + mongo_host+"/csv_load.acquisitions")
        conf.set("spark.mongodb.output.uri","mongodb+srv://" \
                 + mongo_user + ":" + mongo_pwd + "@" + mongo_host+"/csv_load.acquisitions")

        spark = pyspark.sql.SparkSession.builder \
            .appName("BPT-App-MongoDB") \
            .config(conf=conf) \
            .getOrCreate()

    return spark

if __name__ == "__main__":
    run()