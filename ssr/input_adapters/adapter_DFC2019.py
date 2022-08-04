from ssr.config.ssr_config import SSRConfig
from ssr.path_manager import PathManager
from ssr.utility.os_extension import mkdir_safely
from ssr.utility.logging_extension import logger
import os
import tifffile
from osgeo import gdal
import numpy as np
import json
import imageio
import distutils.dir_util


class InputAdapter:
    def __init__(self, pm: PathManager):
        self.pm = pm
        self.config = SSRConfig.get_instance()

    def run(self):
        logger.info("Importing the DFC2019 dataset")
        mkdir_safely(self.pm.rec_pan_png_idp)
        mkdir_safely(self.pm.vissat_meta_data_idp)

        # extract the images and meta information from the tif files
        for index, ifn in enumerate(sorted(os.listdir(self.pm.rgb_tif_idp))):
            current_stem, current_ext = os.path.splitext(ifn)
            if current_ext == ".tif":
                ifp = os.path.join(self.pm.rgb_tif_idp, ifn)
                img, meta = self.parse_tif_image(ifp)

                png_ofp = os.path.join(
                    self.pm.rec_pan_png_idp, f"{index}_{current_stem}.png"
                )
                imageio.imwrite(png_ofp, img)

                json_ofp = os.path.join(
                    self.pm.vissat_meta_data_idp,
                    f"{index}_{current_stem}.json",
                )
                with open(json_ofp, "w") as fp:
                    json.dump(meta, fp, indent=2)
                logger.info(f"Imported {ifn}")

            if current_ext == ".txt":
                # update the config with the correct location metadata based on truth file
                self.read_location_metadata(
                    os.path.join(self.pm.rgb_tif_idp, ifn)
                )

        # if pan sharpening is not enabled, move the images into the correct folder for the following pipeline steps
        if not SSRConfig.get_instance().pan_sharpening:
            mkdir_safely(self.pm.sharpened_with_skew_png_dp)
            distutils.dir_util.copy_tree(
                self.pm.rec_pan_png_idp, self.pm.sharpened_with_skew_png_dp
            )

    def read_location_metadata(self, txt_fp):
        conf = SSRConfig.get_instance()
        if (
            conf.ul_easting is None
            and conf.ul_northing is None
            and conf.width is None
            and conf.height is None
        ):
            # lower left corner
            easting, northing, pixels, gsd = np.loadtxt(txt_fp)
            conf.ul_easting = easting
            conf.ul_northing = northing + (pixels - 1) * gsd
            conf.width = int(pixels) * gsd
            conf.height = int(pixels) * gsd
            logger.info(
                f"Read location metadata: ul_easting={conf.ul_easting}"
            )
            logger.info(
                f"Read location metadata: ul_northing={conf.ul_northing}"
            )
            logger.info(f"Read location metadata: width={conf.width}")
            logger.info(f"Read location metadata: height={conf.height}")

    def parse_tif_image(self, tiff_fp):
        """
        Source: https://github.com/Kai-46/SatelliteSfM/blob/7ea9aebba7cbab586792797c3d65a2c6dca51b8b/preprocess/parse_tif_image.py#L7
        """
        dataset = gdal.Open(tiff_fp, gdal.GA_ReadOnly)
        img = dataset.ReadAsArray()
        assert len(img.shape) == 3 and img.shape[0] == 3
        img = img.transpose((1, 2, 0))  # [c, h, w] --> [h, w, c]
        assert img.dtype == np.uint8

        metadata = dataset.GetMetadata()
        date_time = metadata["NITF_IDATIM"]
        year = int(date_time[0:4])
        month = int(date_time[4:6])
        day = int(date_time[6:8])
        hour = int(date_time[8:10])
        minute = int(date_time[10:12])
        second = int(date_time[12:14])
        capture_date = [year, month, day, hour, minute, second]

        rpc_data = dataset.GetMetadata("RPC")
        rpc_dict = {
            "lonOff": float(rpc_data["LONG_OFF"]),
            "lonScale": float(rpc_data["LONG_SCALE"]),
            "latOff": float(rpc_data["LAT_OFF"]),
            "latScale": float(rpc_data["LAT_SCALE"]),
            "altOff": float(rpc_data["HEIGHT_OFF"]),
            "altScale": float(rpc_data["HEIGHT_SCALE"]),
            "rowOff": float(rpc_data["LINE_OFF"]),
            "rowScale": float(rpc_data["LINE_SCALE"]),
            "colOff": float(rpc_data["SAMP_OFF"]),
            "colScale": float(rpc_data["SAMP_SCALE"]),
            "rowNum": np.asarray(
                rpc_data["LINE_NUM_COEFF"].split(), dtype=np.float64
            ).tolist(),
            "rowDen": np.asarray(
                rpc_data["LINE_DEN_COEFF"].split(), dtype=np.float64
            ).tolist(),
            "colNum": np.asarray(
                rpc_data["SAMP_NUM_COEFF"].split(), dtype=np.float64
            ).tolist(),
            "colDen": np.asarray(
                rpc_data["SAMP_DEN_COEFF"].split(), dtype=np.float64
            ).tolist(),
        }

        meta_dict = {
            "rpc": rpc_dict,
            "height": img.shape[0],
            "width": img.shape[1],
            "capture_date": capture_date,
        }

        return img, meta_dict
