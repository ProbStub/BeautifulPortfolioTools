class PipelineBuilder():
    """
    Builds a SparkML pipeline according to user instructions, applying
    custom transforms as required
    """

    def __init__(self, custom_tf=None):
        """
        Create a pipeline builder

        Args:
            custom_tf: Dict with an instance of the SparkML custom transformer and a
                        dict for the transformer parameters, eg.
                        {myStringDecimalTransformer: {myStringDecimalTransformer.removeTokens: "'",
                                                      myStringDecimalTransformer.decSplitStr: "."}}
        Raises:
            ValueError: If custom_tf does not contain instances to prevent zip() from overwriting named parameters
        """

        transformers, params = zip(*custom_tf.items())
        transformers = list(transformers)
