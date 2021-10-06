import os
import io

from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.sql import functions as F
import chardet

def load_file(file_name, spark_session):
    """
    Loads an indicated file after inspection into a spark session

    Args:
        file_name: String of a fully qualified path to a file

    Returns:
        Raw Spark dataframe, no schema inference of any types to avoid file re-scan

    Raises:
        # TODO: Several errors, eg. not found, access, format, bad input (size/row counts...) TBD

    """

    _allowed_ft = ["csv"]
    _allowed_cd = ["utf-8", "ascii"]

    spark = spark_session

    file_type = __get_type__(file_name)
    file_enc = __get_encoding__(file_name)


    # Only load files for which a load procedure has been implemented
    if file_type in _allowed_ft and file_enc in _allowed_cd:
        # No inference of schema to avoid rescans
        return_df = spark.read.csv(file_name)

    return return_df

def __get_type__(file_name):
    """
    Inspect the file_name string to determine the file type based on characters after the last dot (".")
    Args:
        file_name: String of a fully qualified path to a file

    Returns:
        The string after the last dot ("."). None otherwise

    """
    _type = None

    _type = file_name.split(".")[-1]

    return _type

def __get_encoding__(file_name):
    """
    Inspect the file encoding format

    Args:
        file_name: String of a fully qualified path to a file

    Returns:
        A string representing the encoding format, e.g, "utf-8". Otherwise None

    """
    _encoding = None

    file_byte = io.open(file_name, "rb").read()
    _encoding = chardet.detect(file_byte)

    return _encoding["encoding"]



