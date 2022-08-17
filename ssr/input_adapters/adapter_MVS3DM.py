from ssr.config.ssr_config import SSRConfig
from ssr.path_manager import PathManager
from ssr.config.vissat_config import (
    create_vissat_extraction_config,
)
from ssr.utility.logging_extension import logger
from ssr.utility.os_extension import mkdir_safely
from stereo_pipeline import StereoPipeline as VisSatStereoPipeline


class InputAdapter:
    def __init__(self, pm: PathManager):
        self.pm = pm
        self.config = SSRConfig.get_instance()

    def run(self, run_input_adapter=True):
        if run_input_adapter:
            logger.info("Importing the MVS3DM dataset")

            # execute the first two steps of the vissat pipeline to prepare the dataset
            dataset_dp = self.config.satellite_image_pan_dp
            workspace_dp = self.config.workspace_vissat_dp
            mkdir_safely(workspace_dp)
            create_vissat_extraction_config(
                vissat_config_ofp=self.pm.vissat_config_fp,
                dataset_dp=dataset_dp,
                workspace_dp=workspace_dp,
                ssr_config=self.config,
            )
            pipeline = VisSatStereoPipeline(self.pm.vissat_config_fp)
            pipeline.run()
