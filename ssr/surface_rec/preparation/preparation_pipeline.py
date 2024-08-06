from distutils.dir_util import copy_tree
from distutils.file_util import copy_file
from ssr.utility.os_extension import mkdir_safely
from ssr.utility.os_extension import makedirs_safely


from ssr.surface_rec.preparation.data_extraction.extraction_pipeline import (
    ExtractionPipeline,
)
from ssr.config.ssr_config import SSRConfig
from ssr.surface_rec.preparation.depth_map_recovery.depth_map_recovery import (
    recover_depth_maps,
)
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
        geo_crop_coordinates_list=None,
    ):

        pipeline = ExtractionPipeline(pan_or_msi_config_fp)
        extracted_crops = pipeline.run(
            ift,
            oft,
            execute_parallel,
            remove_aux_file,
            apply_tone_mapping,
            joint_tone_mapping,
            geo_crop_coordinates_list=geo_crop_coordinates_list,
        )
        return extracted_crops

    def run(
        self,
        depth_map_recovery=True,
        skew_correction=True,
    ):

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
