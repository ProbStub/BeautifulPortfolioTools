from itertools import chain

from pyspark.ml import Pipeline
from pyspark.sql import SparkSession


class PipelineRunner:

    """
    Executes a SparkML pipeline created by a PipelineBuilder and records monitoring
    and execution parameters selected by the user (e.g., storing intermittent dataframes
    or recording specific size/volume parameters for each transform).
    """

    # TODO: Decide on logging calls to centralized here, in a logging component or ad-hoc in builders/transformers

    def __init__(self, spark_df, spark_session, pb_list):
        """
        Initiates a PipelineRunner based on an existing spark session and pipeline configurations

        Args:
            spark_df: Spark dataframe
            spark_session: Spark session
            pb_list: A list of PipelineBuilders of any type
        """
        # TODO: Enable logging "spark.eventLog.enabled true" write to mondgodb with a time index
        # TODO: Runtime spark context configuration, e.g, log level & location based on size/type of PipelineBuilders

        self.pb_list = []

        # Only add non empty specified pipelines for execution
        for pipeline_builder in pb_list:
            if len(pipeline_builder.params) >= 1 and \
                    len(pipeline_builder.transformers) >= 1:
                self.pb_list.append(pipeline_builder)
        if len(self.pb_list) == 0:
            raise ValueError("PipelineRunner: Cannot create pipeline runner from an empty PipelineBuilder")

        self.in_df = spark_df
        self.spark = spark_session

        self.pipeline = self.stage(pb_list)

    @staticmethod
    def extract_transformer(pb_list):
        """
        Return a list of transformer instances form a PipelineBuilder

        Args:
            pb_list: A PipelineBuilder

        Returns:
            List of SparkML transformer instances

        """
        transformer_lists = list((o.transformers for o in pb_list))
        transformer_lists_items = list(chain(*transformer_lists))

        return transformer_lists_items

    @staticmethod
    def extract_params(pb_list):
        """
        Return a list of parameter dicts form a PipelineBuilder

        Args:
            pb_list: A PipelineBuilder

        Returns:
            List of SparkML parameter dicts

        """
        params_lists = list(o.params for o in pb_list)
        params_lists_items = list(chain(*params_lists))

        # FIXME: Need to return ParaMap but of ALL pb_list not just the first, so chain is wrong here ;)
        return params_lists_items[0]

    def stage(self, pb_list):
        """
        Order pipeline builder by priority and build a Pipeline object

        Returns:
            A SparkML Pipeline with priority ordered transformer stages

        """
        pb_list.sort(key=lambda x: x.priority, reverse=True)
        pipe_transformer = self.extract_transformer(pb_list)

        return_pipe = Pipeline(stages=pipe_transformer)

        return return_pipe

    def execute(self):
        """
        Execute fit and transform on the properly ordered SparkML Pipeline stages

        Returns:
            A Spark Dataframe

        """

        return_df = self.pipeline.fit(self.in_df, self.extract_params(self.pb_list)).transform(self.in_df)

        return return_df

    def __start_spark__():
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
