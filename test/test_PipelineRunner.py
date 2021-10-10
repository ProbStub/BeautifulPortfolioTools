from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.ml.param import Param

import CustomTransformers
from PipelineBuilder import PipelineBuilder
from PipelineRunner import PipelineRunner


class TestPipelineRunner:
    def init(self):
        self.test_spark = self.__start_spark__()
        self.test_df = self.__create_test_df__()
        test_transform1 = CustomTransformers.TitleFoldTransformer(
            inputCol="aCol",
            outputCol="aCollOut",
            capLength=1,
            strSep=" ")
        test_params1 = test_transform1.extractParamMap()
        test_transform2 = CustomTransformers.TitleFoldTransformer(
            inputCol="bCol",
            outputCol="bColOut",
            capLength=2,
            strSep=" ")
        test_params2 = test_transform2.extractParamMap()

        test_transform3 = CustomTransformers.TitleFoldTransformer(
            inputCol="xCol",
            outputCol="xCollOut",
            capLength=3,
            strSep=" ")
        test_params3 = test_transform3.extractParamMap()
        test_transform4 = CustomTransformers.TitleFoldTransformer(
            inputCol="yCol",
            outputCol="yColOut",
            capLength=4,
            strSep=" ")
        test_params4 = test_transform4.extractParamMap()

        test_transform_list1 = [test_transform1, test_transform2]
        test_transform_list2 = [test_transform3, test_transform4]
        test_params_list1 = [test_params1, test_params2]
        test_params_list2 = [test_params3, test_params4]
        self.test_pipe_build1 = PipelineBuilder(custom_tf=test_transform_list1,
                                                custom_params=test_params_list1,
                                                priority=2)
        self.test_pipe_build2 = PipelineBuilder(custom_tf=test_transform_list2,
                                                custom_params=test_params_list2,
                                                priority=1)
        self.test_runner = PipelineRunner(spark_df=self.test_df,
                                          spark_session=self.test_spark,
                                          pb_list=[self.test_pipe_build1, self.test_pipe_build1])


    def test_extract_transformer_two_pb(self):
        self.init()
        test_result = self.test_runner.extract_transformer([self.test_pipe_build1, self.test_pipe_build2])
        assert len(test_result) == 4 and \
               type(test_result) == list and \
               test_result[0].__class__.__base__.__name__ == "Transformer"

    def test_extract_params_one_pb(self):
        self.init()
        test_result = self.test_runner.extract_params([self.test_pipe_build1])
        assert len(test_result) == 8 and \
               type(test_result) == dict and \
               all([type(k) is Param for k in test_result])

    def test_extract_params_two_pb(self):
        self.init()
        test_result = self.test_runner.extract_params([self.test_pipe_build1, self.test_pipe_build2])
        assert len(test_result) == 16 and \
               type(test_result) == dict and \
               all([type(k) is Param for k in test_result])

    def test_stage(self):
        self.init()

    def test_execute(self):
        self.init()

    def __start_spark__(self):
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

    def __create_test_df__(self):

        data = [(3000, "Name", "Peter", "gh56-lje5-8763", "Male"),
                (3000, "Age", "20 years", "fh65-lkew-1263", "Male"),
                (4000, "Name", "Conny", "pl41-hje9-4729", "Female"),
                (4000, "Age", "21 years", "1h57-6jeq-g76w", "Female"),
                (5000, "Name", "Rosi", "pl41-hje9-4729", "Female"),
                (5000, "Age", "21 years", "1h27-6jeq-g76w", "Female"),
                (6000, "Name", "Max", "pl41-h1e9-4729", "Male"),
                (6000, "Age", "22 years", "1h57-6jfq-g76w", "Male"),
                (7000, "Name", "Thomas", "pl41-mje9-4729", "Male"),
                (7000, "Age", "27 years", "1hn7-6jeq-g76w", "Male")
                ]

        schema = StructType([ \
            StructField("PivKey", IntegerType(), True), \
            StructField("PivName", StringType(), True), \
            StructField("PivValues", StringType(), True), \
            StructField("RecordKey", StringType(), True), \
            StructField("OtherAttribute1", StringType(), True) \
            ])

        test_df = self.test_spark.createDataFrame(data=data, schema=schema)

        return test_df

