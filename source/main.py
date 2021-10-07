import os
from dotenv import load_dotenv

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType

import FileUtility as fu
from PipelineBuilderLoad import PipelineBuilderLoad


def run():
    """
    Program initiation function parsing user parameters, providing help and launching the application

    Returns:
        -

    """
    # TODO: Add user parameter parsing and basic help output

    print("Initiating...")
    load_dotenv()

    # TODO: Pre-Release remove mongod DB dependency!!
    mongo_host = os.getenv("MONGO_HOST")
    mongo_user = os.getenv("MONGO_USER")
    mongo_pwd = os.getenv("MONGO_PWD")

    pg_host = os.getenv("PG_HOST")
    pg_user = os.getenv("PG_USER")
    pg_pwd = os.getenv("PG_PWD")

    spark = __start_mongo_spark__(mongo_host, mongo_user, mongo_pwd)

    # df_mdb = spark.read.format("mongo").load()
    # df_pg = df_mdb.select("_c0","_c9").withColumn("id",F.col("_c0").cast(IntegerType())).withColumnRenamed("_c9","content").drop(F.col("_c0"))
    # df_pg.write \
    #     .format("jdbc") \
    #     .option("url", "jdbc:postgresql://" + pg_host + "/spark_mongo") \
    #     .option("driver", "org.postgresql.Driver") \
    #     .option("dbtable", "input.objects") \
    #     .option("user", "postgres") \
    #     .option("password", pg_pwd) \
    #     .mode("append") \
    #     .save()
    # Prepare and load input (from file storage)
    # TODO: replace local file load with Kaggle -> GCS -> load implementation for test runs
    raw_df = fu.load_file("/opt/data/ETFs.csv", spark)
    # TODO: Configuration of Pipeline Builder for ETF load
    load_pipe = PipelineBuilderLoad(auto_schema=True, auto_correct=True)
    # TODO: Execute PipelineRunner for ETFs
    # Prepare and safe output (to mongodb, instruments and market data are evolving schema)

    # Prepare and load input (from mongodb)
    # TODO: Configure and Execute Pipeline* for portfolio building (excl. Investment Policy Statement)
    # Prepare and load input (from mongodb and postgres, IPS and user data are fixed schema)
    # TODO: Configure and Execute Pipeline* for portfolio building (incl. Investment Policy Statement constraints)
    # Prepare and safe output

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
    if mongo_host is None or mongo_user is None or mongo_pwd is None:
        raise RuntimeError("Cannot start MongoDB connection due to missing connection/login credentials.")
    else:
        # Note: MongoDB Atlas -> mongodb+srv and no ports! Using mongo-spark connector 3.0.1
        # verify package JARs download to cluster nodes -> check logs for :: resolving dependencies ::
        # Also DB=sample_analytics, Collection=Customers
        # TODO: move package choice to PipelineRunner (a load pipeline may not need mongodb without logging)
        # TODO: Enable Dynamic Allocation
        conf = pyspark.SparkConf()
        conf.set("spark.jars.packages",
                 "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1,org.postgresql:postgresql:42.2.22")
        conf.set("spark.mongodb.input.uri", "mongodb+srv://" \
                 + mongo_user + ":" + mongo_pwd + "@" + mongo_host+"/csv_load.acquisitions")
        conf.set("spark.mongodb.output.uri","mongodb+srv://" \
                 + mongo_user + ":" + mongo_pwd + "@" + mongo_host+"/csv_load.acquisitions")

        spark = pyspark.sql.SparkSession.builder \
            .appName("BPT-App-Spark-Mongo") \
            .config(conf=conf) \
            .getOrCreate()

    return spark

def __start_postgres_spark__(pg_host, pg_user, pg_pwd):
    if pg_host is None or pg_user is None or pg_pwd is None:
        raise RuntimeError("Cannot start Postgres connection due to missing connection/login credentials.")
    else:
        conf = pyspark.SparkConf()
        conf.set("spark.jars.packages", "org.postgresql:postgresql:42.2.22")
        spark = pyspark.sql.SparkSession.builder \
            .appName("BPT-App-Postgres") \
            .config(conf=conf) \
            .getOrCreate()

    return spark


if __name__ == "__main__":
    run()
