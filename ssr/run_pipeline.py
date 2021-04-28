import os
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

from ssr.config.ssr_config import SSRConfig


def check_vissat_workspace(self, pm):
    if not os.path.isdir(pm.rec_pan_png_idp):
        logger.vinfo("pm.rec_pan_png_idp", pm.rec_pan_png_idp)
        assert False


def create_config_from_template(config_template_ifp, config_fp):
    config_template_ifp = os.path.abspath(config_template_ifp)
    config_fp = os.path.abspath(config_fp)

    if not os.path.isfile(config_fp):
        copyfile(config_template_ifp, config_fp)
    return SSRConfig(config_fp=config_fp)


def create_path_manager(ssr_config):
    pm = PathManager(
        pan_ntf_idp=ssr_config.get_option_value("satellite_image_pan_dp", str),
        msi_ntf_idp=ssr_config.get_option_value("satellite_image_msi_dp", str),
        vissat_workspace_dp=ssr_config.get_option_value(
            "workspace_vissat_dp", str
        ),
        ssr_workspace_dp=ssr_config.get_option_value(
            "workspace_ssr_dp", str
        ),
    )
    return pm


def create_backend_manager(ssr_config):
    bm = BackendManager()
    bm.set_meshing_backends(
        ssr_config.get_option_value("meshing_backends", list)
    )
    bm.set_texturing_backends(
        ssr_config.get_option_value("texturing_backends", list)
    )
    return bm


if __name__ == "__main__":

    ssr_config_template_ifp = "./configs/pipeline_template.cfg"
    ssr_config_fp = "./configs/pipeline.cfg"
    ssr_config = create_config_from_template(
        ssr_config_template_ifp, ssr_config_fp
    )
    SSRConfig.set_instance(ssr_config)

    pm = create_path_manager(ssr_config)
    bm = create_backend_manager(ssr_config)

    # =====
    # Gather options from the config file
    # =====
    lazy = ssr_config.get_option_value("lazy", bool)
    # === SfM / MVS Options ===
    reconstruct_sfm_mvs = ssr_config.get_option_value(
        "reconstruct_sfm_mvs", bool
    )
    # === Preparation Options ===
    extract_pan = ssr_config.get_option_value("extract_pan", bool)
    extract_msi = ssr_config.get_option_value("extract_msi", bool)
    pan_sharpening = ssr_config.get_option_value("pan_sharpening", bool)
    depth_map_recovery = ssr_config.get_option_value(
        "depth_map_recovery", bool
    )
    skew_correction = ssr_config.get_option_value("skew_correction", bool)
    # === Meshing Options ===
    reconstruct_mesh = ssr_config.get_option_value("reconstruct_mesh", bool)
    # === Texturing Options ===
    texture_mesh = ssr_config.get_option_value("texture_mesh", bool)

    # =====
    # Run the pipeline
    # =====
    vissat_pipeline = VisSatPipeline(pm)
    vissat_pipeline.run(reconstruct_sfm_mvs)

    pm.check_rec_pan_png_idp()
    preparation_pipeline = PreparationPipeline(pm)
    preparation_pipeline.run(
        extract_pan=extract_pan,
        extract_msi=extract_msi,
        pan_sharpening=pan_sharpening,
        depth_map_recovery=depth_map_recovery,
        skew_correction=skew_correction,
    )

    surface_reconstruction_pipeline = SurfaceReconstructionPipeline(pm, bm)
    surface_reconstruction_pipeline.run(
        reconstruct_mesh=reconstruct_mesh,
        texture_mesh=texture_mesh,
        lazy=lazy,
    )
