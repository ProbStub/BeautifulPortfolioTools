from pyspark.ml import Pipeline

from PipelineBuilder import PipelineBuilder


class PipelineBuilderLoad(PipelineBuilder):
    """
    Builds a SparkML data loading pipeline according to user instructions, applying
    custom transforms as required (e.g., fully automated schema and type
    inference or choosing imputation methods) by inspection of a Spark
    dataframe
    """

    # TODO: Manage property exposure once class design completes

    def __init__(self, auto_schema, auto_correct, custom_tf=[], custom_params=[]):
        """
        Create a pipeline builder either with automatic schema inference and imputation/correction
        enabled or a defines set of transformers to be executed.

        Args:
            auto_schema: Set to True in case automatic schema inference is required, False otherwise
            auto_correct: Set to True in case automatic schema inference is required, False otherwise
            List of dicts with transformer parameters such as
                            {myStringDecimalTransformer.removeTokens: "'",
                             myStringDecimalTransformer.decSplitStr: "."}}
        """

        # TODO: Clean up this constructor and remove actions on data and ensure all object attributes are set...

        if auto_schema:
            # TODO: coordinate Transformers for schema inference, then add to custom_tf and custom_params
            if len(custom_tf) > 1:
                custom_tf.append([])
            if len(custom_params) > 1:
                custom_params.append([])
        if auto_correct:
            # TODO: coordinate Transformers for cleaning, then add to custom_tf and custom_params
            if len(custom_tf) > 1:
                custom_tf.append([])
            if len(custom_params) > 1:
                custom_params.append([])

        # build and fit the pipleline
        super().__init__(custom_tf=custom_tf,
                         custom_params=custom_params)
