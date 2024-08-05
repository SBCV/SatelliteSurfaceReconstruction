import os
import sys
from shutil import copyfile
from ssr.utility.logging_extension import logger
from ssr.path_manager import PathManager
from ssr.sfm_mvs_rec.vissat_pipeline import VisSatPipeline
from ssr.surface_rec.preparation.preparation_pipeline import (
    PreparationPipeline,
)
from ssr.surface_rec.surface.surface_reconstruction_pipeline import (
    SurfaceReconstructionPipeline,
)
from ssr.surface_rec.backends.backend_manager import (
    BackendManager,
)
from ssr.input_adapters.run_input_adapter import RunInputAdapterPipeline
from ssr.utility.os_extension import makedirs_safely
from ssr.config.ssr_config import SSRConfig


def check_imageio_freeimage_plugin_installation():
    import imageio

    try:
        # https://github.com/imageio/imageio/blob/master/imageio/plugins/_freeimage.py
        imageio.plugins._freeimage.get_freeimage_lib()
    except imageio.core.NeedDownloadError:
        msg = "Imageio can not find the Freeimage plugin."
        msg += " See instructions above for installation."
        assert False, msg


def check_vissat_workspace(self, pm):
    if not os.path.isdir(pm.rec_pan_png_idp):
        logger.vinfo("pm.rec_pan_png_idp", pm.rec_pan_png_idp)
        assert False


def create_config_from_template(config_template_ifp, config_fp):
    config_template_ifp = os.path.abspath(config_template_ifp)
    config_fp = os.path.abspath(config_fp)

    if not os.path.isfile(config_fp):
        copyfile(config_template_ifp, config_fp)
    ssr_config = SSRConfig.get_from_file(config_fp)
    ssr_config.check_paths_for_potential_errors()
    return ssr_config


if __name__ == "__main__":

    check_imageio_freeimage_plugin_installation()

    ssr_config_template_ifp = "./configs/pipeline_template.toml"
    ssr_config_fp = "./configs/pipeline.toml"

    # check if a config was optionally passed as command line argument
    if len(sys.argv) > 1:
        ssr_config_fp = sys.argv[1]

    ssr_config = create_config_from_template(
        ssr_config_template_ifp, ssr_config_fp
    )

    SSRConfig.set_instance(ssr_config)
    ssr_config.read_missing_aoi_data()

    pm = PathManager(
        pan_ntf_idp=ssr_config.satellite_image_pan_dp,
        msi_ntf_idp=ssr_config.satellite_image_msi_dp,
        rgb_tif_idp=ssr_config.satellite_image_rgb_tif_dp,
        aoi_specific_idn=ssr_config.aoi_specific_idn,
        vissat_workspace_root_dp=ssr_config.workspace_vissat_root_dp,
        ssr_workspace_root_dp=ssr_config.workspace_ssr_root_dp,
        meshlab_temp_root_dp=ssr_config.meshlab_temp_root_dp,
        adapter=ssr_config.dataset_adapter,
        aoi_name=ssr_config.aoi_name,
        zone_number=ssr_config.zone_number,
        hemisphere=ssr_config.hemisphere,
        ul_easting=ssr_config.ul_easting,
        ul_northing=ssr_config.ul_northing,
    )
    bm = BackendManager(
        meshing_backends=ssr_config.meshing_backends,
        texturing_backends=ssr_config.texturing_backends,
    )

    makedirs_safely(pm.vissat_workspace_dp)
    makedirs_safely(pm.ssr_workspace_dp)
    makedirs_safely(pm.meshlab_temp_dp)

    input_adapter_pipeline = RunInputAdapterPipeline(pm)
    input_adapter_pipeline.run(
        dataset_adapter=ssr_config.dataset_adapter,
        run_input_adapter=ssr_config.run_input_adapter,
    )

    vissat_pipeline = VisSatPipeline(pm)
    vissat_pipeline.init_vissat()
    vissat_pipeline.run(ssr_config.reconstruct_sfm_mvs)

    pm.check_rec_pan_png_idp()
    preparation_pipeline = PreparationPipeline(pm)
    preparation_pipeline.run(
        extract_pan=ssr_config.extract_pan,
        extract_msi=ssr_config.extract_msi,
        pan_sharpening=ssr_config.pan_sharpening,
        depth_map_recovery=ssr_config.depth_map_recovery,
        skew_correction=ssr_config.skew_correction,
    )

    surface_reconstruction_pipeline = SurfaceReconstructionPipeline(pm, bm)
    surface_reconstruction_pipeline.run(
        reconstruct_mesh=ssr_config.reconstruct_mesh,
        texture_mesh=ssr_config.texture_mesh,
        lazy=ssr_config.lazy,
    )
