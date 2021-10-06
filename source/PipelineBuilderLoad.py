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

    def __init__(self, auto_schema, auto_correct, custom_tf=None, custom_params=None):
        """
        Create a pipeline builder either with automatic schema inference and imputation/correction
        enabled or a defines set of transformers to be executed.

        Args:
            auto_schema: Set to True in case automatic schema inference is required, False otherwise
            auto_correct: Set to True in case automatic schema inference is required, False otherwise
            custom_tra: Dict with an instance of the SparkML custom transformer and a
                        dict for the transformer parameters, eg.
                        {myStringDecimalTransformer: {myStringDecimalTransformer.removeTokens: "'",
                                                      myStringDecimalTransformer.decSplitStr: "."}}
        """
        if auto_schema:
            # TODO: coordinate Transformers for schema inference, then add to custom_tf and custom_params
            custom_tf.append(None)
        if auto_correct:
            # TODO: coordinate Transformers for cleaning, then add to custom_tf and custom_params
            custom_tf.append(None)
        # build and fit the pipleline
        super().__init__(self,
                         custom_tf,
                         custom_tf,
                         custom_params)
