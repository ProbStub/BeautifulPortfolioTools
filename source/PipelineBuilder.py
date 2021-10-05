class PipelineBuilder():
    """
    Builds a SparkML pipeline according to user instructions, applying
    custom transforms as required (e.g., fully automated schema and type
    inference or choosing imputation methods) by inspection of a Spark
    dataframe
    """