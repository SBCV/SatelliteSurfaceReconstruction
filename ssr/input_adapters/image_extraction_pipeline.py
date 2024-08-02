import os
from ssr.utility.os_extension import mkdir_safely
from ssr.config.ssr_config import SSRConfig
from ssr.config.vissat_config import (
    create_vissat_extraction_config,
)
from ssr.surface_rec.preparation.data_extraction.extraction_pipeline import (
    ExtractionPipeline,
)


class ImageExtractionPipeline:
    def __init__(self, pm):
        self.pm = pm
        self.ssr_config = SSRConfig.get_instance()

    @staticmethod
    def extract_files(
        pan_or_msi_config_fp,
        ift,
        oft,
        execute_parallel,
        remove_aux_file,
        apply_tone_mapping,
        joint_tone_mapping,
        geo_crop_coordinates_list=None
    ):

        pipeline = ExtractionPipeline(pan_or_msi_config_fp)
        extracted_crops = pipeline.run(
            ift,
            oft,
            execute_parallel,
            remove_aux_file,
            apply_tone_mapping,
            joint_tone_mapping,
            geo_crop_coordinates_list=geo_crop_coordinates_list
        )
        return extracted_crops

    def extract_msi(self, pm, oft, execute_parallel, remove_aux_file, apply_tone_mapping, joint_tone_mapping):
        mkdir_safely(pm.msi_workspace_dp)
        create_vissat_extraction_config(
            pm.msi_config_fp,
            pm.msi_ntf_idp,
            pm.msi_workspace_dp,
            self.ssr_config,
        )
        assert os.path.isfile(pm.msi_config_fp)

        msi_geo_crops = self.extract_files(
            pm.msi_config_fp,
            ift="MSI",
            oft=oft,
            execute_parallel=execute_parallel,
            remove_aux_file=remove_aux_file,
            apply_tone_mapping=apply_tone_mapping,
            joint_tone_mapping=joint_tone_mapping,
            geo_crop_coordinates_list=None,
        )
        return msi_geo_crops

    def extract_pan(self, pm, oft, execute_parallel, remove_aux_file, apply_tone_mapping, joint_tone_mapping,
                    msi_geo_crop_coordinate_list=None):
        mkdir_safely(pm.pan_workspace_dp)
        create_vissat_extraction_config(
            vissat_config_ofp=pm.pan_config_fp,
            dataset_dp=pm.pan_ntf_idp,
            workspace_dp=pm.pan_workspace_dp,
            ssr_config=self.ssr_config,
        )
        assert os.path.isfile(pm.pan_config_fp)

        pan_geo_crops = self.extract_files(
            pm.pan_config_fp,
            ift="PAN",
            oft=oft,
            execute_parallel=execute_parallel,
            remove_aux_file=remove_aux_file,
            apply_tone_mapping=apply_tone_mapping,
            joint_tone_mapping=joint_tone_mapping,
            geo_crop_coordinates_list=msi_geo_crop_coordinate_list
        )
        return pan_geo_crops

    def run(
        self,
        extract_msi_pan_image_pairs=True,
        use_consistent_msi_pan_extraction=True
    ):
        if not extract_msi_pan_image_pairs:
            return
        # === Additional options for extract_pan and extract_msi === #
        oft = "png"
        remove_aux_file = False
        apply_tone_mapping = True
        joint_tone_mapping = (
            False  # Separate tone mapping yields much better results
        )
        execute_parallel = True

        pm = self.pm
        mkdir_safely(pm.ssr_workspace_dp)

        msi_geo_crop_coordinate_list = self.extract_msi(
            pm,
            oft,
            execute_parallel,
            remove_aux_file,
            apply_tone_mapping,
            joint_tone_mapping,
        )

        if not use_consistent_msi_pan_extraction:
            msi_geo_crop_coordinate_list = None

        self.extract_pan(
            pm,
            oft,
            execute_parallel,
            remove_aux_file,
            apply_tone_mapping,
            joint_tone_mapping,
            msi_geo_crop_coordinate_list
        )
