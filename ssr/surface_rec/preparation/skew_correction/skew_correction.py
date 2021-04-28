import os
import numpy as np
import copy
from PIL import Image as PILImage
import imageio
import cv2

from ssr.utility.os_extension import mkdir_safely
from ssr.ssr_types.camera import Camera
from ssr.file_handler.colmap_file_handler import ColmapFileHandler

from ssr.surface_rec.preparation.depth_map_recovery.depth_map_recovery import (
    parse_depth_map,
)
from ssr.surface_rec.preparation.depth_map_recovery.depth_map_recovery import (
    write_depth_map,
)

from ssr.ext.read_write_model import read_cameras_text

# See Paper:
#   Leveraging Vision Reconstruction Pipelines for Satellite Imagery
#   ICCV Workshops 2019
from ssr.utility.logging_extension import logger


def remove_skew_from_images_legazy(pil_image, image_invert_skew_mat):
    # Own experiments showed that the opencv warping function produced lower
    # errors than pillow warping method

    # https://pillow.readthedocs.io/en/stable/reference/Image.html
    # https://stackoverflow.com/questions/17056209/python-pil-affine-transformation
    #   PIL REQUIRES THE INVERSE MATRIX FOR THE TRANSFORMATION

    skew_mat = np.linalg.inv(image_invert_skew_mat)

    affine_trans_params = list(skew_mat.flatten())[0:6]
    pil_image_transformed = pil_image.transform(
        pil_image.size,
        PILImage.AFFINE,
        data=affine_trans_params,
        resample=PILImage.BICUBIC,
    )
    return pil_image_transformed


def fix_affine_matrix(original_mat):
    # Fix cv2 affine warping matrix offset
    # https://github.com/opencv/opencv/issues/4585
    # https://github.com/opencv/opencv/issues/11784

    fixed_mat = original_mat.copy()
    fixed_mat[0, 2] += (fixed_mat[0, 0] + fixed_mat[0, 1]) / 2.0 - 0.5
    fixed_mat[1, 2] += (fixed_mat[1, 0] + fixed_mat[1, 1]) / 2.0 - 0.5
    return fixed_mat


def remove_skew_from_matrix(
    data_mat,
    remove_skew_mat,
    use_inverse_warping=False,
    interpolation_type=cv2.INTER_CUBIC,
):
    # https://github.com/SBCV/open3d_colormap_opt_z_buffering/blob/update_to_open3d_0_10/demo.py
    assert interpolation_type in [cv2.INTER_NEAREST, cv2.INTER_CUBIC]

    remove_skew_mat_top_rows = remove_skew_mat[0:2]
    assert remove_skew_mat_top_rows[0, 0] == 1
    assert remove_skew_mat_top_rows[0, 1] != 0
    assert remove_skew_mat_top_rows[0, 2] == 0
    assert remove_skew_mat_top_rows[1, 0] == 0
    assert remove_skew_mat_top_rows[1, 1] == 1
    assert remove_skew_mat_top_rows[1, 2] == 0

    flags = interpolation_type  # cv2.INTER_CUBIC
    if use_inverse_warping:
        # https://towardsdatascience.com/image-geometric-transformation-in-numpy-and-opencv-936f5cd1d315
        #   Read the section about "Inverse Warping"
        flags += cv2.WARP_INVERSE_MAP

        # Compute the inverse of the skew matrix without numerical errors,
        # i.e. instead of "remove_skew_mat = np.linalg.inv(remove_skew_mat)"
        # use the following:
        remove_skew_mat[0, 1] = -remove_skew_mat[0, 1]
    else:
        pass

    # Fix cv2 affine warping matrix offset
    remove_skew_mat_top_rows = fix_affine_matrix(remove_skew_mat_top_rows)

    data_mat_skew_free = cv2.warpAffine(
        data_mat,
        remove_skew_mat_top_rows,
        (data_mat.shape[1], data_mat.shape[0]),
        flags=flags,
        # possible values for borderMode:
        #   cv2.BORDER_REPLICATE, cv2.BORDER_CONSTANT
        # Must use cv2.BORDER_CONSTANT for skew. Otherwise huge areas get
        # incorrect depth values.
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )

    return data_mat_skew_free


def get_corresponding_depth_map_fn(image_ifn, depth_map_type="geometric"):
    return image_ifn + "." + depth_map_type + ".bin"


def compute_skew_free_camera_models(
    colmap_model_with_skew_idp,
    gray_image_with_skew_idp,
    color_image_with_skew_idp,
    depth_map_with_skew_idp,
    colmap_model_no_skew_odp,
    gray_image_no_skew_odp,
    color_image_no_skew_odp,
    depth_map_no_skew_odp,
    perform_warping_evaluation=False,
    interpolation_type=cv2.INTER_CUBIC,
):
    assert colmap_model_with_skew_idp != colmap_model_no_skew_odp
    assert gray_image_with_skew_idp != gray_image_no_skew_odp
    assert depth_map_with_skew_idp != depth_map_no_skew_odp

    if gray_image_no_skew_odp is not None:
        mkdir_safely(gray_image_no_skew_odp)

    if color_image_no_skew_odp is not None:
        mkdir_safely(color_image_no_skew_odp)

    if depth_map_no_skew_odp is not None:
        mkdir_safely(depth_map_no_skew_odp)

    logger.vinfo("image_without_skew_odp", gray_image_no_skew_odp)
    logger.vinfo("interpolation_type", interpolation_type)

    cameras = ColmapFileHandler.parse_colmap_cams(
        colmap_model_with_skew_idp, gray_image_with_skew_idp
    )
    # cameras, _ = ColmapFileHandler.parse_colmap_model_folder(
    #   colmap_model_idp, image_idp
    # )

    num_cameras = len(cameras)
    skew_free_camera_list = []

    pil_better_count = 0
    mat_better_count = 0
    patt_count = 0
    for camera in cameras:
        logger.vinfo("camera.id", str(camera.id) + " of " + str(num_cameras))
        logger.vinfo("camera.file_name", camera.file_name)

        intrinsic_mat = camera.get_calibration_mat()
        (
            skew_mat,
            intrinsic_mat_wo_skew,
        ) = Camera.compute_intrinsic_skew_decomposition(intrinsic_mat)
        image_invert_skew_mat = np.linalg.inv(skew_mat)

        image_ifn = camera.file_name
        image_stem, ext = os.path.splitext(image_ifn)

        if gray_image_with_skew_idp is not None:

            image_ifp = os.path.join(gray_image_with_skew_idp, image_ifn)
            mat_image_ofp = os.path.join(
                gray_image_no_skew_odp, image_stem + ext
            )

            mat_image = imageio.imread(image_ifp)
            mat_image_transformed = remove_skew_from_matrix(
                mat_image,
                image_invert_skew_mat,
                interpolation_type=interpolation_type,
            )
            imageio.imwrite(mat_image_ofp, mat_image_transformed)

        if color_image_with_skew_idp is not None:
            image_ifp = os.path.join(color_image_with_skew_idp, image_ifn)
            mat_image_ofp = os.path.join(
                color_image_no_skew_odp, image_stem + ext
            )

            mat_image = imageio.imread(image_ifp)
            mat_image_transformed = remove_skew_from_matrix(
                mat_image,
                image_invert_skew_mat,
                interpolation_type=interpolation_type,
            )
            imageio.imwrite(mat_image_ofp, mat_image_transformed)

        if depth_map_with_skew_idp is not None:
            depth_map_fn = get_corresponding_depth_map_fn(image_ifn)
            depth_ifp = os.path.join(depth_map_with_skew_idp, depth_map_fn)
            depth_ofp = os.path.join(depth_map_no_skew_odp, depth_map_fn)

            depth_mat = parse_depth_map(depth_ifp)
            depth_mat_transformed = remove_skew_from_matrix(
                depth_mat,
                image_invert_skew_mat,
                interpolation_type=interpolation_type,
            )
            write_depth_map(depth_mat_transformed, depth_ofp)

        # if perform_warping_evaluation:
        #
        #     logger.info('--------------------- Diffs --------------------')
        #
        #     mat_image_recovered_mat = np.array(
        #       remove_skew_from_matrix(mat_image_transformed, skew_mat)
        #     )
        #     mat_image_diff_mat = np.abs(mat_image - mat_image_recovered_mat)
        #     mat_image_error_ofp = os.path.join(
        #       gray_image_no_skew_odp, image_stem + '_mat_error' + ext
        #     )
        #     imageio.imwrite(mat_image_error_ofp, mat_image_diff_mat)
        #     mat_diff = np.nansum(mat_image_diff_mat)
        #     logger.vinfo('mat_diff', mat_diff)
        #
        #     # pil_image = PILImage.open(image_ifp)
        #     # pil_image_transformed = remove_skew_from_images_legazy(
        #           pil_image, image_invert_skew_mat
        #       )
        #     # pil_image_transformed.save(pil_image_ofp)
        #     #
        #     # pil_image_recovered_mat = np.array(
        #           remove_skew_from_images_legazy(
        #               pil_image_transformed, skew_mat
        #           )
        #       )
        #     # pil_image_mat = np.array(pil_image)
        #     # pil_image_diff_mat = np.abs(
        #           pil_image_mat - pil_image_recovered_mat
        #       )
        #     # pil_image_error_ofp = os.path.join(
        #           image_without_skew_odp, image_stem + '_pil_error' + ext
        #       )
        #     # imageio.imwrite(pil_image_error_ofp, pil_image_diff_mat)
        #     # pil_diff = np.nansum(pil_image_diff_mat)
        #     # logger.vinfo('pil_diff', pil_diff)
        #     #
        #     # if pil_diff > mat_diff:
        #     #     mat_better_count += 1
        #     # elif mat_diff > pil_diff:
        #     #     pil_better_count += 1
        #     # else:
        #     #     patt_count += 1

        skew_free_camera = copy.copy(camera)
        skew_free_camera.set_calibration(
            intrinsic_mat_wo_skew, radial_distortion=False
        )
        skew_free_camera_list.append(skew_free_camera)

    if perform_warping_evaluation:
        logger.vinfo("pil_better_count", pil_better_count)
        logger.vinfo("mat_better_count", mat_better_count)
        logger.vinfo("patt_count", patt_count)

    if colmap_model_no_skew_odp is not None:
        mkdir_safely(colmap_model_no_skew_odp)
        ColmapFileHandler.write_colmap_cameras(
            odp=colmap_model_no_skew_odp,
            cameras=skew_free_camera_list,
            colmap_camera_model_name="PINHOLE",
        )


if __name__ == "__main__":

    compute_skew_free_camera_models(
        colmap_model_with_skew_idp="/path/to/colmap/sfm_perspective/tri_ba",
        gray_image_with_skew_idp="/path/to/colmap/mvs/images",
        colmap_model_no_skew_odp="/path/to/workspace/temp",
        gray_image_no_skew_odp="/path/to/workspace/images_pan",
    )
