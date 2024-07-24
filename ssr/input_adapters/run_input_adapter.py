import importlib
from ssr.utility.logging_extension import logger


class RunInputAdapterPipeline:
    def __init__(self, pm, preparation_pipeline=None):
        self.pm = pm
        self.preparation_pipeline = preparation_pipeline

    def run(self, dataset_adapter, run_input_adapter=True):
        if run_input_adapter:
            logger.vinfo(
                "Running dataset preprocessing using the following adapter",
                dataset_adapter,
            )
            dataset_adapter = f"ssr.input_adapters.{dataset_adapter}"
            adapter_file = importlib.import_module(dataset_adapter)
            adapter = getattr(adapter_file, "InputAdapter")(self.pm, self.preparation_pipeline)
            adapter.run()
