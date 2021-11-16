class PipelineBuilder:

    """
    Builds a SparkML pipeline according to user instructions, applying
    custom transforms as required
    """
    # TODO: Manage property exposure once class design completes
    def __init__(self, custom_tf=None, custom_params=None, priority=0):
        """
        Create SparkML Pipeline configuration including the selected transformers and parameters

        Args:
            custom_tf: List of transformer instances
            custom_params: List of dicts with transformer parameters such as
                            {myStringDecimalTransformer.removeTokens: "'",
                             myStringDecimalTransformer.decSplitStr: "."}

        """

        # TODO: Add facilities, e.g., ogging, error handling, parameter structure checks, priority, model registry, etc.
        if custom_params is None:
            custom_params = []
        if custom_tf is None:
            custom_tf = []
        self.transformers = custom_tf
        self.params = custom_params
        self.priority = priority
