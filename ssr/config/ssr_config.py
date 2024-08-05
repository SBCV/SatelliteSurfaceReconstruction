import toml
import numpy as np
from pydantic import BaseModel
from typing import List, Union
import os
from ssr.utility.logging_extension import logger

_config = None


class VisSatConfig(BaseModel):
    clean_data: Union[bool, int] = False
    crop_image: Union[bool, int] = False
    derive_approx: Union[bool, int] = True
    choose_subset: Union[bool, int] = True
    colmap_sfm_perspective: Union[bool, int] = True
    inspect_sfm_perspective: Union[bool, int] = True
    reparam_depth: Union[bool, int] = True
    colmap_mvs: Union[bool, int] = True
    aggregate_2p5d: Union[bool, int] = True
    aggregate_3d: Union[bool, int] = True


class SSRConfig(BaseModel):
    colmap_vissat_exe_fp: str
    colmap_vissat_lib_dp: str
    texrecon_apps_dp: str
    meshlab_server_fp: str
    colmap_exe_dp: str
    gdmr_bin_dp: str
    mve_apps_dp: str
    openmvs_bin_dp: str

    satellite_image_pan_dp: str = ""
    satellite_image_msi_dp: str = ""
    satellite_image_rgb_tif_dp: str = ""
    satellite_aoi_data_dp: str = ""

    aoi_specific_idn: str = ""

    workspace_vissat_root_dp: str
    workspace_ssr_root_dp: str
    meshlab_temp_root_dp: str

    dataset_adapter: str
    aoi_name: str = ""
    zone_number: int
    hemisphere: str
    ul_easting: float = None
    ul_northing: float = None
    width: float = None
    height: float = None
    aoi_data_fn: str = None
    alt_min: float
    alt_max: float

    meshing_backends: List[str]
    texturing_backends: List[str]

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

    vis_sat_config: VisSatConfig = VisSatConfig()

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
        potential_invalid_paths = []
        for name in attrs:
            if name.endswith("_dp"):
                if not os.path.isdir(attrs[name]):
                    potential_invalid_paths.append(name)
            if name.endswith("_fp"):
                if not os.path.isfile(attrs[name]):
                    potential_invalid_paths.append(name)

        logger.info(
            "The following config entry may not have been set correctly:"
        )
        for name in potential_invalid_paths:
            logger.info(f"  {name} = {attrs[name]}")

    def read_missing_aoi_data(self):
        if (
            self.ul_easting is None
            and self.ul_northing is None
            and self.width is None
            and self.height is None
        ):
            msg = (
                "Either provide the variables ul_easting, ul_northing, "
                "width and height or satellite_aoi_data_dp and "
                "aoi_data_fn in the config file."
            )
            assert self.satellite_aoi_data_dp is not None, msg
            assert self.aoi_data_fn is not None, msg

            # lower left corner
            txt_ifp = os.path.join(
                self.satellite_aoi_data_dp,
                self.aoi_specific_idn,
                self.aoi_data_fn,
            )

            assert os.path.isfile(txt_ifp), txt_ifp
            easting, northing, pixels, gsd = np.loadtxt(txt_ifp)
            self.ul_easting = easting
            self.ul_northing = northing + (pixels - 1) * gsd
            self.width = int(pixels) * gsd
            self.height = int(pixels) * gsd
            logger.info(f"Read location metadata:")
            logger.info(f"  ul_easting = {self.ul_easting}")
            logger.info(f"  ul_northing = {self.ul_northing}")
            logger.info(f"  width = {self.width}")
            logger.info(f"  height = {self.height}")
