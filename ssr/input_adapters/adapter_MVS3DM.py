from ssr.config.ssr_config import SSRConfig
from ssr.path_manager import PathManager
from ssr.utility.logging_extension import logger


class InputAdapter:
    def __init__(self, pm: PathManager, preparation_pipeline=None):
        self.pm = pm
        self.preparation_pipeline = preparation_pipeline
        self.config = SSRConfig.get_instance()

    def run(self):
        logger.info("Importing the MVS3DM dataset")

        if self.config.extract_msi_pan_image_pairs and self.preparation_pipeline is not None:
            self.preparation_pipeline.extract_msi_pan_image_pairs(
                extract_msi_pan_image_pairs=self.config.extract_msi_pan_image_pairs,
                use_consistent_msi_pan_extraction=self.config.use_consistent_msi_pan_extraction,
            )
