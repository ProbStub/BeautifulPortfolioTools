from PipelineBuilder import PipelineBuilder


class PipelineRunner(PipelineBuilder):
    """
    Executes a SparkML pipeline created by a PipelineBuilder and records monitoring
    and execution parameters selected by the user (e.g., storing intermittent dataframes
    or recording specific size/volume parameters for each transform).
    """
    # TODO: Decide on logging calls to centralized here, in a logging component or ad-hoc in builders/transformers