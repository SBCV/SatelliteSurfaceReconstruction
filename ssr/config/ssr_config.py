import toml
from pydantic import BaseModel
from typing import List, Union
import os
from ssr.utility.logging_extension import logger

_config = None


class SSRConfig(BaseModel):
    colmap_vissat_exe_fp: str
    colmap_vissat_lib_dp: str
    texrecon_apps_dp: str
    meshlab_server_fp: str
    meshlab_temp_dp: str
    colmap_exe_dp: str
    gdmr_bin_dp: str
    mve_apps_dp: str
    openmvs_bin_dp: str

    satellite_image_pan_dp: str = ""
    satellite_image_msi_dp: str = ""
    satellite_image_rgb_tif_dp: str = ""
    workspace_vissat_dp: str
    workspace_ssr_dp: str

    zone_number: int
    hemisphere: str
    ul_easting: float = None
    ul_northing: float = None
    width: float = None
    height: float = None
    alt_min: float
    alt_max: float

    meshing_backends: List[str]
    texturing_backends: List[str]

    dataset_adapter: str
    reconstruct_sfm_mvs: Union[bool, int]
    run_input_adapter: Union[bool, int]
    extract_msi: Union[bool, int] = False
    extract_pan: Union[bool, int] = False
    pan_sharpening: Union[bool, int] = False
    depth_map_recovery: Union[bool, int]
    skew_correction: Union[bool, int]

    reconstruct_mesh: Union[bool, int]
    texture_mesh: Union[bool, int]

    lazy: Union[bool, int] = False

    @staticmethod
    def get_instance():
        assert _config is not None
        return _config

    @staticmethod
    def set_instance(config):
        global _config
        _config = config

    @classmethod
    def get_from_file(cls, toml_ifp):
        config_dict = toml.load(toml_ifp)
        return cls(**config_dict)

    def check_paths_for_potential_errors(self):
        attrs = vars(self)
        for name in attrs:
            if name.endswith("_dp"):
                if not os.path.isdir(attrs[name]):
                    logger.vinfo(
                        "The following config entry may not have been set correctly",
                        f"{name}={attrs[name]}",
                    )
            if name.endswith("_fp"):
                if not os.path.isfile(attrs[name]):
                    logger.vinfo(
                        "The following config entry may not have been set correctly",
                        f"{name}={attrs[name]}",
                    )
