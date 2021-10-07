from pyspark.ml import Pipeline

class PipelineBuilder():
    """
    Builds a SparkML pipeline according to user instructions, applying
    custom transforms as required
    """

    # TODO: Manage property exposure once class design completes

    def __init__(self, custom_tf=[], custom_params=[]):
        """
        Create a fit()ed pipeline including the selected transformers and parameters

        Args:
            custom_tf: List of transformer instances
            custom_params: List of dicts with transformer parameters such as
                            {myStringDecimalTransformer.removeTokens: "'",
                             myStringDecimalTransformer.decSplitStr: "."}}

        """

        # TODO: Add Builder facilities such as logging, error handling, parameter dict structure checks, etc.
        # TODO: Clean up this constructor and remove actions on data and ensure all object attributes are set...

        if len(custom_tf) > 1 or len(custom_params) > 1:
            self.transformers = custom_tf
            self.params = custom_params
            self.pipeline = Pipeline(stages=[self.transformers])
        else:
            # Composing empty instance to retain pipeline facilities get/setParams for manual setting of
            # pipeline parameters
            self.pipeline = Pipeline()
