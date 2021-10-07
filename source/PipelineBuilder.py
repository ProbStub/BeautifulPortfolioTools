class PipelineBuilder():
    """
    Builds a SparkML pipeline according to user instructions, applying
    custom transforms as required
    """

    # TODO: Manage property exposure once class design completes

    def __init__(self, custom_tf=[], custom_params=[], priority=0):
        """
        Create  SparkML Pipeline including the selected transformers and parameters

        Args:
            custom_tf: List of transformer instances
            custom_params: List of dicts with transformer parameters such as
                            {myStringDecimalTransformer.removeTokens: "'",
                             myStringDecimalTransformer.decSplitStr: "."}}

        """

        # TODO: Add facilities such as logging, error handling, parameter dict structure checks, priority etc.
        self.transformers = custom_tf
        self.params = custom_params
        self.priority = priority
