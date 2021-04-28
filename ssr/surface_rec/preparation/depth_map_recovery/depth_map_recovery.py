import os
import numpy as np
from ssr.utility.os_extension import get_file_paths_in_dir
from ssr.ext.read_dense import read_array
from ssr.ext.read_write_dense import write_array
from ssr.file_handler.ply_file_handler import PLYFileHandler
from ssr.file_handler.colmap_file_handler import ColmapFileHandler
from ssr.types.point import Point
from ssr.utility.os_extension import mkdir_safely

# from ssr.types.python_cache import PythonCache
from ssr.utility.logging_extension import logger
from ssr.types.camera import Camera


def contains_nan(array):
    return np.isnan(np.sum(array))


def parse_last_rows(last_rows_ifp):
    last_rows = {}
    with open(last_rows_ifp) as fp:
        for line in fp.readlines():
            tmp = line.split(" ")
            img_name = tmp[0]
            last_row = np.array([float(tmp[i]) for i in range(1, 5)])
            last_rows[img_name] = last_row
    return last_rows


def parse_depth_range(depth_range_ifp):
    depth_ranges = {}
    with open(depth_range_ifp) as fp:
        fp.readline()  # read comment line
        for line in fp.readlines():
            tmp = line.split(" ")
            img_name = tmp[0]
            depth_range = np.array([float(tmp[i]) for i in range(1, 3)])
            depth_ranges[img_name] = depth_range
    return depth_ranges


def parse_inv_proj_mats(inv_proj_mat_ifp):
    inv_proj_mats = {}
    with open(inv_proj_mat_ifp) as fp:
        for line in fp.readlines():
            tmp = line.split(" ")
            img_name = tmp[0]
            mats = np.array([float(tmp[i]) for i in range(1, 17)]).reshape(
                (4, 4)
            )
            inv_proj_mats[img_name] = mats
    return inv_proj_mats


def compute_extended_proj_and_inv_proj_mat(camera, last_row, value_range=10):

    # Follow the projection matrix computation here:
    #   https://github.com/Kai-46/ColmapForVisSat/blob/master/src/mvs/image.cc#L75

    proj_mat_3_x_4 = camera.get_4x4_world_to_cam_mat()[0:3, 0:4]

    proj_mat_3_x_4 = np.dot(camera.get_calibration_mat(), proj_mat_3_x_4)
    proj_mat_4_x_4 = np.vstack((proj_mat_3_x_4, last_row))

    proj_scaling_factor = 1.0
    overall_inv_proj_scaling_factor = 1.0

    if value_range is not None:
        proj_scaling_factor = value_range / np.amax(proj_mat_4_x_4)
        proj_mat_4_x_4 = proj_mat_4_x_4 * proj_scaling_factor

    inv_proj_mat_4_x_4 = np.linalg.inv(proj_mat_4_x_4)
    if value_range is not None:
        inv_proj_scaling_factor = value_range / np.amax(inv_proj_mat_4_x_4)
        inv_proj_mat_4_x_4 = inv_proj_mat_4_x_4 * inv_proj_scaling_factor
        overall_inv_proj_scaling_factor = (
            inv_proj_scaling_factor / proj_scaling_factor
        )

    return (
        proj_mat_4_x_4,
        inv_proj_mat_4_x_4,
        proj_scaling_factor,
        overall_inv_proj_scaling_factor,
    )


def parse_depth_map(depth_map_fp):
    depth_map = read_array(depth_map_fp)
    contains_nan_value = contains_nan(depth_map)
    # logger.info(depth_map_fp + ' contains nan: ' + str(contains_nan_value))
    depth_map[depth_map <= 0.0] = np.nan  # actually it is -1e20
    return depth_map


def write_depth_map(depth_map, depth_map_ofp):
    depth_map_copy = depth_map.copy()
    depth_map_copy = np.nan_to_num(depth_map_copy, nan=-1e20)
    write_array(depth_map_copy, depth_map_ofp)


def convert_reparameterized_depth_map_to_world_points(
    depth_map_reparameterized, inv_proj_mat
):
    # https://github.com/Kai-46/VisSatSatelliteStereo/blob/master/aggregate_2p5d_util.py

    height, width = depth_map_reparameterized.shape
    row, col = np.meshgrid(range(height), range(width), indexing="ij")
    # reshape((1, -1)) converts the two dimensional array (height, width) into
    # an array (1, height * width)
    col = col.reshape((1, -1))
    row = row.reshape((1, -1))
    depth = depth_map_reparameterized.reshape((1, -1))

    # Project from depth values to scene space, following the c++ fusion code
    #   https://github.com/Kai-46/ColmapForVisSat/blob/master/src/mvs/fusion.cc#L429
    # The next line is consistent with the left vector in eq. (8) on page 5
    uv1m = np.vstack((col, row, np.ones((1, width * height)), depth))
    # P^{-1} [u, v, 1, m]^T = [x/Z, y/Z, z/Z, 1/Z]^T
    hom_world_points = np.dot(inv_proj_mat, uv1m)
    hom_world_points[0, :] /= hom_world_points[3, :]
    hom_world_points[1, :] /= hom_world_points[3, :]
    hom_world_points[2, :] /= hom_world_points[3, :]
    valid_mask = np.logical_not(np.isnan(hom_world_points[2, :]))
    coords = hom_world_points[:, valid_mask].T
    return coords


def convert_reparameterized_depth_map_to_real_depth_map(
    depth_map_reparam, inv_proj_mat, inv_scaling_factor
):
    # depth_map_reparameterized contains nan for invalid depth values
    height, width = depth_map_reparam.shape
    row, col = np.meshgrid(range(height), range(width), indexing="ij")
    # reshape((1, -1)) converts the two dimensional array (height, width) into
    # an array (1, height * width)
    col = col.reshape((1, -1))
    row = row.reshape((1, -1))
    depth_map_reparam_1d = depth_map_reparam.reshape((1, -1))

    # Project from depth values to scene space, following the c++ fusion code
    #   https://github.com/Kai-46/ColmapForVisSat/blob/master/src/mvs/fusion.cc#L429
    # The next line is consistent with the left vector in eq. (8) on page 5
    uv1m = np.vstack(
        (col, row, np.ones((1, width * height)), depth_map_reparam_1d)
    )
    # P^{-1} [u, v, 1, m]^T = [x/Z, y/Z, z/Z, 1/Z]^T
    hom_world_points = np.dot(inv_proj_mat, uv1m)

    inverse_z_values = hom_world_points[3, :]
    z_values = inv_scaling_factor / inverse_z_values
    z_values = z_values.astype(np.float32)
    depth_map_real = z_values.reshape(height, width)

    return depth_map_real


def recover_depth_maps(
    model_with_skew_idp,
    last_rows_ifp,
    image_with_skew_idp,
    depth_map_reparam_with_skew_idp,
    depth_map_real_with_skew_odp,
    depth_map_type="geometric",
    # Optional parameters
    check_inv_proj_mat=False,
    inv_proj_mat_ifp=None,
    check_depth_mat_storing=False,
    create_depth_map_point_cloud=False,
    depth_map_point_cloud_odp=None,
    create_depth_map_point_cloud_reference=False,
    depth_map_point_cloud_reference_odp=None,
):

    mkdir_safely(depth_map_real_with_skew_odp)

    if create_depth_map_point_cloud:
        mkdir_safely(depth_map_point_cloud_odp)
    if create_depth_map_point_cloud_reference:
        mkdir_safely(depth_map_point_cloud_reference_odp)

    assert depth_map_type in ["geometric", "photometric"]

    inv_proj_mats = None
    if check_inv_proj_mat:
        inv_proj_mats = parse_inv_proj_mats(inv_proj_mat_ifp)

    last_rows = parse_last_rows(last_rows_ifp)

    depth_map_suffix = "." + depth_map_type + ".bin"
    depth_map_reparam_ifp_list = get_file_paths_in_dir(
        depth_map_reparam_with_skew_idp,
        ext=".bin",
        target_str_or_list=depth_map_suffix,
    )

    cameras, points3D = ColmapFileHandler.parse_colmap_model_folder(
        model_with_skew_idp, image_with_skew_idp
    )
    # cache = PythonCache()
    # cameras, points3D = cache.get_cached_result(
    #     callback=ColmapFileHandler.parse_colmap_model_folder,
    #     params=[model_with_skew_idp, image_with_skew_idp],
    #     unique_id_or_path=1,
    # )

    depth_map_semantic = Camera.DEPTH_MAP_WRT_CANONICAL_VECTORS

    logger.vinfo("depth_map_real_with_skew_odp", depth_map_real_with_skew_odp)

    for camera in cameras[::-1]:
        img_name = camera.file_name

        logger.vinfo("img_name", img_name)

        depth_map_name = img_name + "." + depth_map_type + ".bin"
        depth_map_reparam_with_skew_ifp = os.path.join(
            depth_map_reparam_with_skew_idp, depth_map_name
        )
        depth_map_real_with_skew_ofp = os.path.join(
            depth_map_real_with_skew_odp, depth_map_name
        )

        depth_map_point_cloud_ofp = None
        if create_depth_map_point_cloud:
            depth_map_point_cloud_ofp = os.path.join(
                depth_map_point_cloud_odp, depth_map_name + ".ply"
            )

        depth_map_point_cloud_reference_ofp = None
        if create_depth_map_point_cloud_reference:
            depth_map_point_cloud_reference_ofp = os.path.join(
                depth_map_point_cloud_reference_odp, depth_map_name + ".ply"
            )

        if not depth_map_reparam_with_skew_ifp in depth_map_reparam_ifp_list:
            logger.vinfo(
                "depth_map_reparam_with_skew_ifp",
                depth_map_reparam_with_skew_ifp,
            )
            assert False

        last_row = last_rows[img_name]
        (
            _,
            extended_inv_proj_mat_4_x_4,
            _,
            inv_proj_scaling_factor,
        ) = compute_extended_proj_and_inv_proj_mat(camera, last_row)

        if check_inv_proj_mat:
            extended_inv_proj_mat_4_x_4_reference = inv_proj_mats[img_name]
            np.testing.assert_allclose(
                extended_inv_proj_mat_4_x_4,
                extended_inv_proj_mat_4_x_4_reference,
            )

        # Positions with invalid depth values contain nan
        depth_map_reparam_with_skew = parse_depth_map(
            depth_map_reparam_with_skew_ifp
        )

        depth_map_real_with_skew = (
            convert_reparameterized_depth_map_to_real_depth_map(
                depth_map_reparam_with_skew,
                extended_inv_proj_mat_4_x_4,
                inv_proj_scaling_factor,
            )
        )

        write_depth_map(depth_map_real_with_skew, depth_map_real_with_skew_ofp)

        depth_map_real_with_skew_loaded = parse_depth_map(
            depth_map_real_with_skew_ofp
        )
        if check_depth_mat_storing:
            np.testing.assert_allclose(
                depth_map_real_with_skew, depth_map_real_with_skew_loaded
            )

        depth_mean_val = np.nanmean(depth_map_real_with_skew_loaded)
        logger.vinfo("depth_mean_val", depth_mean_val)

        if create_depth_map_point_cloud:
            cam_coords = camera.convert_depth_map_to_cam_coords(
                depth_map_real_with_skew,
                depth_map_semantic,
                shift_to_pixel_center=False,  # Must be false
                depth_map_display_sparsity=100,
            )
            logger.vinfo(
                "cam_to_world_mat: ", camera.get_4x4_cam_to_world_mat()
            )
            world_coords = camera.cam_to_world_coord_multiple_coords(
                cam_coords
            )
            points = Point.get_points_from_coords(world_coords)
            PLYFileHandler.write_ply_file(depth_map_point_cloud_ofp, points)

        if create_depth_map_point_cloud_reference:
            coords_reference = (
                convert_reparameterized_depth_map_to_world_points(
                    depth_map_reparam_with_skew, extended_inv_proj_mat_4_x_4
                )
            )
            points_reference = Point.get_points_from_coords(coords_reference)
            PLYFileHandler.write_ply_file(
                depth_map_point_cloud_reference_ofp, points_reference
            )
