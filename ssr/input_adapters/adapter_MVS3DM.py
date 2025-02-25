from ssr.config.ssr_config import SSRConfig
from ssr.input_adapters.image_extraction_pipeline import ImageExtractionPipeline
from ssr.path_manager import PathManager
from ssr.utility.logging_extension import logger
from ssr.utility.os_extension import assert_dirs_equal
from ssr.gdal_utility.pan_sharpening import perform_pan_sharpening_for_folder


class InputAdapter:
    def __init__(self, pm: PathManager):
        self.pm = pm
        self.config = SSRConfig.get_instance()

    def run(self):
        logger.info("Importing the MVS3DM dataset")

        if self.config.extract_msi_pan_image_pairs:
            image_extraction_pipeline = ImageExtractionPipeline(self.pm)
            image_extraction_pipeline.run(
                use_consistent_msi_pan_extraction=self.config.use_consistent_msi_pan_extraction,
            )

        if self.config.pan_sharpening:
            resampling_algorithm = "cubic"
            perform_pan_sharpening_for_folder(
                self.pm.pan_png_idp,
                self.pm.msi_png_idp,
                self.pm.sharpened_with_skew_png_dp,
                resampling_algorithm=resampling_algorithm,
                check_consistent_msi_pan_extraction=self.config.use_consistent_msi_pan_extraction,
            )
