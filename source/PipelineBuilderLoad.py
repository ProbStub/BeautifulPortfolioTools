from CustomTransformers import StringDecimalTransformer
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
        super().__init__()

        self.auto_schema = auto_schema
        self.auto_correct = auto_correct

        self.transformers = custom_tf
        self.params = custom_params

        if self.auto_schema:
            # TODO: coordinate Transformers for schema inference, then add to custom_tf and custom_params
            sdt = StringDecimalTransformer(inputCol = "_c0",
                  outputCol = " _t0",
                  removeTokens = ["'"],
                  decSplitStr = ".",
                  precision = 10,
                  scale = 4)
            if len(self.transformers) >= 1:
                self.transformers.append(sdt)
            else:
                self.transformers = [sdt]
            if len(self.params) >= 1:
                self.params.append(sdt.extractParamMap())
            else:
                self.params = [sdt.extractParamMap()]

        if self.auto_correct:
            # TODO: coordinate Transformers for cleaning, then add to custom_tf and custom_params
            if len(self.transformers) >= 1:
                self.transformers.append("TransformerX")
            else:
                self.transformers = "TransformerX"
            if len(self.params) >= 1:
                self.params.append("ParamsX")
            else:
                self.params = "ParamsX"


