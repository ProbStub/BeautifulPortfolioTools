from pyspark.ml import Pipeline

class PipelineBuilder():
    """
    Builds a SparkML pipeline according to user instructions, applying
    custom transforms as required
    """

    # TODO: Manage property exposure once class design completes

    def __init__(self, input_df, custom_tf=None, custom_params=None):
        """
        Create a fit()ed pipeline including the selected transformers and parameters

        Args:
            custom_tf: List of transformer instances
            custom_params: List of dicts with transformer parameters

        """

        if custom_tf is not None or custom_params is not None:
            self.transformers = custom_tf
            self.params = custom_params
            self.pipeline = Pipeline(stages=[self.transformers]).fit(input_df, self.params)
        else:
            # Composing empty instance to retain pipeline facilities get/setParams for manual setting
            self.pipeline = Pipeline()
