import os
from distutils.dir_util import copy_tree
from distutils.file_util import copy_file
from ssr.utility.os_extension import mkdir_safely
from ssr.utility.os_extension import makedirs_safely
from ssr.utility.os_extension import assert_dirs_equal


from ssr.surface_rec.preparation.data_extraction.extraction_pipeline import (
    ExtractionPipeline,
)
from ssr.config.vissat_config import (
    create_vissat_extraction_config,
)
from ssr.config.ssr_config import SSRConfig
from ssr.surface_rec.preparation.depth_map_recovery.depth_map_recovery import (
    recover_depth_maps,
)
from ssr.gdal_utility.pan_sharpening import perform_pan_sharpening_for_folder
from ssr.surface_rec.preparation.skew_correction.skew_correction import (
    compute_skew_free_camera_models,
)


class PreparationPipeline:
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
    ):

        pipeline = ExtractionPipeline(pan_or_msi_config_fp)
        pipeline.run(
            ift,
            oft,
            execute_parallel,
            remove_aux_file,
            apply_tone_mapping,
            joint_tone_mapping,
        )

    def run(
        self,
        extract_pan=True,
        extract_msi=True,
        pan_sharpening=True,
        depth_map_recovery=True,
        skew_correction=True,
    ):

        # =================================================================
        # Prerequisites (ORDER MATTERS):
        #   1. Reconstruct mesh with PAN images
        #   2. Extract corresponding MSI images
        #   3. Compute PAN Sharpened Images
        #   4. Compute Skew Corrected Camera Models and Skew Corrected PAN
        #      Sharpened Images
        # ================================================================

        # === Additional options for extract_pan and extract_msi === #
        oft = "png"
        remove_aux_file = False
        apply_tone_mapping = True
        joint_tone_mapping = (
            False  # Separate tone mapping yields much better results
        )
        execute_parallel = True

        # === Additional options for pan_sharpening === #
        resampling_algorithm = "cubic"
        pm = self.pm
        mkdir_safely(pm.ssr_workspace_dp)

        if extract_pan:
            mkdir_safely(pm.pan_workspace_dp)
            create_vissat_extraction_config(
                vissat_config_ofp=pm.pan_config_fp,
                dataset_dp=pm.pan_ntf_idp,
                workspace_dp=pm.pan_workspace_dp,
                ssr_config=self.ssr_config,
            )
            assert os.path.isfile(pm.pan_config_fp)

            PreparationPipeline.extract_files(
                pm.pan_config_fp,
                ift="PAN",
                oft=oft,
                execute_parallel=execute_parallel,
                remove_aux_file=remove_aux_file,
                apply_tone_mapping=apply_tone_mapping,
                joint_tone_mapping=joint_tone_mapping,
            )

            assert_dirs_equal(pm.pan_png_idp, pm.rec_pan_png_idp)

        if extract_msi:
            mkdir_safely(pm.msi_workspace_dp)
            create_vissat_extraction_config(
                pm.msi_config_fp,
                pm.msi_ntf_idp,
                pm.msi_workspace_dp,
                self.ssr_config,
            )
            PreparationPipeline.extract_files(
                pm.msi_config_fp,
                ift="MSI",
                oft=oft,
                execute_parallel=execute_parallel,
                remove_aux_file=remove_aux_file,
                apply_tone_mapping=apply_tone_mapping,
                joint_tone_mapping=joint_tone_mapping,
            )

        if pan_sharpening:
            assert_dirs_equal(pm.pan_png_idp, pm.rec_pan_png_idp)
            perform_pan_sharpening_for_folder(
                pm.rec_pan_png_idp,
                pm.msi_png_idp,
                pm.sharpened_with_skew_png_dp,
                resampling_algorithm=resampling_algorithm,
            )

        if depth_map_recovery:
            makedirs_safely(pm.depth_map_real_with_skew_dp)
            recover_depth_maps(
                model_with_skew_idp=pm.sparse_model_with_skew_idp,
                last_rows_ifp=pm.last_rows_ifp,
                image_with_skew_idp=pm.sharpened_with_skew_png_dp,
                depth_map_reparam_with_skew_idp=pm.depth_map_reparam_with_skew_idp,
                depth_map_real_with_skew_odp=pm.depth_map_real_with_skew_dp,
                depth_map_type="geometric",
                # Optional parameters
                check_inv_proj_mat=False,
                inv_proj_mat_ifp=None,
                check_depth_mat_storing=False,
                create_depth_map_point_cloud=False,
                depth_map_point_cloud_odp=None,
                create_depth_map_point_cloud_reference=False,
                depth_map_point_cloud_reference_odp=None,
            )

        if skew_correction:
            mkdir_safely(pm.sparse_model_no_skew_dp)

            # Copy the original sparse model and overwrite it with the values
            # from the next step
            copy_tree(
                pm.sparse_model_with_skew_idp, pm.sparse_model_no_skew_dp
            )

            compute_skew_free_camera_models(
                colmap_model_with_skew_idp=pm.sparse_model_with_skew_idp,
                gray_image_with_skew_idp=pm.rec_pan_png_idp,
                color_image_with_skew_idp=pm.sharpened_with_skew_png_dp,
                depth_map_with_skew_idp=pm.depth_map_real_with_skew_dp,
                colmap_model_no_skew_odp=pm.sparse_model_no_skew_dp,
                gray_image_no_skew_odp=pm.pan_no_skew_png_dp,
                color_image_no_skew_odp=pm.sharpened_no_skew_png_dp,
                depth_map_no_skew_odp=pm.depth_map_real_no_skew_dp,
                perform_warping_evaluation=False,
            )

            # Copy corresponding fused result
            copy_file(pm.fused_ifp, pm.fused_ofp)
            copy_file(pm.fused_vis_ifp, pm.fused_vis_no_skew_ofp)
