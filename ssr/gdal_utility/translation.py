import os
import logging

from ssr.gdal_utility.open import get_image_min_max
from ssr.gdal_utility.run_gdal import run_gdal_cmd


def compute_src_win(in_ntf, bbx_size, ntf_size):
    # =========================
    # See VisSat/image_crop.py
    # =========================

    if bbx_size is not None or ntf_size is not None:
        assert bbx_size is not None and ntf_size is not None

        (ntf_width, ntf_height) = ntf_size
        (ul_col, ul_row, width, height) = bbx_size

        # assert bounding box is completely inside the image
        assert ul_col >= 0
        assert ul_col + width - 1 < ntf_width
        assert ul_row >= 0
        assert ul_row + height - 1 < ntf_height
        logging.info(
            "ntf image to cut: {}, width, height: {}, {}".format(
                in_ntf, ntf_width, ntf_height
            )
        )
        logging.info(
            "cut image bounding box, ul_col, ul_row, width, height: {}, {}, {}, {}".format(
                ul_col, ul_row, width, height
            )
        )
        scrwin_string = "-srcwin {} {} {} {}".format(ul_col, ul_row, width, height)
    else:
        scrwin_string = None

    return scrwin_string


def perform_translation(
    in_ntf,
    hdr_img_ofp,
    ntf_size=None,
    bbx_size=None,
    bands=None,
    ot="UInt16",
    scale_params=None,
    tone_mapping=None,
    exponent=None,
    a_srs_string=None,
    remove_aux_file=False,
):
    # If scale_params is omitted the output range is 0 to 255

    # ================================================================================
    # Use QGIS to examine the result (i.e. color range of the created file)
    # ================================================================================

    assert not ((scale_params is not None) and (tone_mapping is not None))

    cmd = "gdal_translate"

    if bands is not None:
        for band in bands:
            cmd += " -b " + str(band)

    # Output Format (of)
    #   https://gdal.org/programs/gdal_translate.html
    #       Starting with GDAL 2.3, if not specified, the format is guessed
    #       from the extension (previously was GTiff)
    #   https://gdal.org/programs/raster_common_options.html#raster-common-options-formats
    #       Supported (output) formats
    #           E.g. gdal_translate --formats
    of = os.path.splitext(hdr_img_ofp)[1][1:]
    logging.info("of: {}".format(of))
    cmd += " -of " + of
    cmd += " -ot " + ot

    if scale_params is not None:
        assert len(scale_params) in [0, 2, 4]
        cmd += " -scale"
        for scale_param in scale_params:
            cmd += " " + str(scale_param)

        # TODO
        # https://gdal.org/programs/gdal_translate.html#cmdoption-gdal-translate-exponent
        # To apply non-linear scaling with a power function

    if tone_mapping:
        ntf_min, ntf_max = get_image_min_max(in_ntf)
        cmd += " -scale {} {} {} {}".format(ntf_min, ntf_max, 0, 65536)

    scrwin_string = compute_src_win(in_ntf, bbx_size, ntf_size)
    if scrwin_string is not None:
        cmd += " " + scrwin_string

    if a_srs_string is not None:
        cmd += " -a_srs " + a_srs_string

    cmd += " {} {}".format(in_ntf, hdr_img_ofp)
    run_gdal_cmd(cmd)

    if remove_aux_file and of.lower() == "png":
        aux_xml_path = "{}.aux.xml".format(hdr_img_ofp)
        os.remove(aux_xml_path)
