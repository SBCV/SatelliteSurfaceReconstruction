import os
import subprocess
from ssr.utility.logging_extension import logger
from ssr.utility.os_extension import get_corresponding_files_in_directories
from ssr.utility.os_extension import mkdir_safely


def perform_pan_sharpening(
    pan_ifp, msi_ifp, ofp, resampling_algorithm="cubic"
):
    # https://gdal.org/programs/gdal_pansharpen.html
    # https://gis.stackexchange.com/questions/270476/pansharpening-using-gdal-tools
    #   GDAL pan sharpening algorithm = weighted Brovey algorithm

    ext = os.path.splitext(ofp)[1]
    of = ext[1:]

    call_params = ["gdal_pansharpen.py"]
    call_params += ["-of", of, "-r", resampling_algorithm]

    call_params += [pan_ifp, msi_ifp, ofp]
    logger.vinfo("call_params", call_params)
    sharp_process = subprocess.Popen(call_params)
    sharp_process.wait()


def perform_pan_sharpening_for_folder(
    pan_idp, msi_idp, odp, resampling_algorithm="cubic", check_consistent_msi_pan_extraction=False,
):

    # The created files are using the PAN (AND NOT THE MSI) STEM (i.e. P1BS
    # instead of M1BS) so they can directly be used to replace the original
    # PAN images
    mkdir_safely(odp)

    def get_correspondence_callback(pan_fn):
        # PAN example name: 0001_WV03_15JAN05_135727-P1BS-500497282040_01_P001.png
        # MSI example name: 0001_WV03_15JAN05_135727-M1BS-500497282040_01_P001.png

        pan_parts = pan_fn.split("-P1BS-", 1)
        msi_fn = pan_parts[0] + "-M1BS-" + pan_parts[1]
        return msi_fn

    pan_list, msi_list = get_corresponding_files_in_directories(
        pan_idp,
        msi_idp,
        get_correspondence_callback=get_correspondence_callback,
    )

    for pan_ifp, msi_ifp in zip(pan_list, msi_list):
        if check_consistent_msi_pan_extraction:
            assert_correct_pan_msi_ratio(pan_ifp, msi_ifp, ratio=4)
        msi_sharpened_ofp = os.path.join(odp, os.path.basename(pan_ifp))
        perform_pan_sharpening(
            pan_ifp,
            msi_ifp,
            msi_sharpened_ofp,
            resampling_algorithm=resampling_algorithm,
        )


def assert_correct_pan_msi_ratio(pan_ifp, msi_ifp, ratio=4):
    import imageio.v3 as iio
    pan_img_shape = iio.improps(pan_ifp).shape
    msi_img_shape = iio.improps(msi_ifp).shape
    assert(pan_img_shape[0] == ratio * msi_img_shape[0] and pan_img_shape[1] == ratio * msi_img_shape[1])


if __name__ == "__main__":

    # ========================= Single File =======================
    # pan_ifp = '/path/to/0001_WV03_15JAN05_135727-P1BS-500497282040_01_P001_PAN.png'
    # msi_ifp = '/path/to/0001_WV03_15JAN05_135727-M1BS-500497282040_01_P001_MSI.png'
    # ofp = 'path/to/0001_WV03_15JAN05_135727-P1BS-500497282040_01_P001_SHARPENED.png'
    #
    # perform_pan_sharpening(
    #     pan_ifp,
    #     msi_ifp,
    #     ofp,
    #     resampling_algorithm='cubic')

    # ========================= Single File =======================
    pan_idp = "/path/to/pan"
    msi_idp = "/path/to/msi"
    odp = "path/to/pansharped"
    check_consistent_msi_pan_extraction = True

    perform_pan_sharpening_for_folder(
        pan_idp,
        msi_idp,
        odp,
        resampling_algorithm="cubic",
        check_consistent_msi_pan_extraction=check_consistent_msi_pan_extraction,
    )
