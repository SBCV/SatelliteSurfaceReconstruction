from ssr.config.ssr_config import SSRConfig
from ssr.input_adapters.image_extraction_pipeline import ImageExtractionPipeline
from ssr.path_manager import PathManager
from ssr.utility.logging_extension import logger


class InputAdapter:
    def __init__(self, pm: PathManager):
        self.pm = pm
        self.config = SSRConfig.get_instance()

    def run(self):
        logger.info("Importing the MVS3DM dataset")

        if self.config.extract_msi_pan_image_pairs:
            image_extraction_pipeline = ImageExtractionPipeline(self.pm)
            image_extraction_pipeline.extract_msi_pan_image_pairs(
                extract_msi_pan_image_pairs=self.config.extract_msi_pan_image_pairs,
                use_consistent_msi_pan_extraction=self.config.use_consistent_msi_pan_extraction,
            )
