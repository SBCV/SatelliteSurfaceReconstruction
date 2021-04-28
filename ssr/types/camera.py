import numpy as np
from ssr.utility.logging_extension import logger
from ssr.types.extrinsics import Extrinsics
from ssr.types.intrinsics import Intrinsics


class Camera(Extrinsics, Intrinsics):

    DEPTH_MAP_WRT_UNIT_VECTORS = "DEPTH_MAP_WRT_UNIT_VECTORS"
    # Vectors where the last component is 1
    DEPTH_MAP_WRT_CANONICAL_VECTORS = "DEPTH_MAP_WRT_CANONICAL_VECTORS"

    def __init__(self, file_name=None, width=None, height=None):

        # Coordinate system defines self._quaternion and self.rotation_mat
        super(Camera, self).__init__()

        # Used for visualization
        self.normal = np.array([0, 0, 0], dtype=float)
        # single color to represent the camera (for example in a ply file)
        self.color = np.array([255, 255, 255], dtype=int)

        self.file_name = file_name

        self.width = width
        self.height = height

        # Differentiate between view/image index and reconstruction index
        self.view_index = None  # This is the index w.r.t. to the input images
        self.camera_index = (
            None  # This is the index w.r.t the reconstructed cameras
        )

        self.depth_map_fp = None
        self.depth_map_callback = None
        self.depth_map_semantic = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        file_name = self.file_name
        if file_name is None:
            file_name = "None"
        return str(
            "Camera: "
            + file_name
            + " "
            + str(self._center)
            + " "
            + str(self.normal)
        )

    def get_file_name(self):
        return self.file_name

    def convert_depth_map_to_cam_coords(
        self,
        depth_map,
        depth_map_semantic,
        shift_to_pixel_center,  # False for Colmap, True for MVE
        depth_map_display_sparsity=100,
    ):

        assert 0 < depth_map_display_sparsity

        height, width = depth_map.shape
        logger.info("height " + str(height))
        logger.info("width " + str(width))

        if self.height == height and self.width == width:
            x_step_size = 1.0
            y_step_size = 1.0
        else:
            x_step_size = self.width / width
            y_step_size = self.height / height
            logger.info("x_step_size " + str(x_step_size))
            logger.info("y_step_size " + str(y_step_size))

        fx, fy, skew, cx, cy = self.split_intrinsic_mat(
            self.get_calibration_mat()
        )
        logger.vinfo("fx, fy, skew, cx, cy: ", str([fx, fy, skew, cx, cy]))

        indices = np.indices((height, width))
        y_index_list = indices[0].flatten()
        x_index_list = indices[1].flatten()

        depth_values = depth_map.flatten()

        assert len(x_index_list) == len(y_index_list) == len(depth_values)

        if shift_to_pixel_center:
            # https://github.com/simonfuhrmann/mve/blob/master/libs/mve/depthmap.cc
            #  math::Vec3f v = invproj * math::Vec3f(
            #       (float)x + 0.5f, (float)y + 0.5f, 1.0f);
            u_index_coord_list = x_step_size * x_index_list + 0.5
            v_index_coord_list = y_step_size * y_index_list + 0.5
        else:
            # https://github.com/colmap/colmap/blob/dev/src/base/reconstruction.cc
            #   COLMAP assumes that the upper left pixel center is (0.5, 0.5)
            #   i.e. pixels are already shifted
            u_index_coord_list = x_step_size * x_index_list
            v_index_coord_list = y_step_size * y_index_list

        # The cannoncial vectors are defined according to p.155 of
        # "Multiple View Geometry" by Hartley and Zisserman using a canonical
        # focal length of 1 , i.e. vec = [(x - cx) / fx, (y - cy) / fy, 1]
        skew_correction = (cy - v_index_coord_list) * skew / (fx * fy)
        x_coords_canonical = (u_index_coord_list - cx) / fx + skew_correction
        y_coords_canonical = (v_index_coord_list - cy) / fy
        z_coords_canonical = np.ones(len(depth_values), dtype=float)

        # Determine non-background data
        # non_background_flags = np.logical_not(np.isnan(depth_values))
        depth_values_not_nan = np.nan_to_num(depth_values)
        non_background_flags = depth_values_not_nan > 0

        x_coords_canonical_filtered = x_coords_canonical[non_background_flags]
        y_coords_canonical_filtered = y_coords_canonical[non_background_flags]
        z_coords_canonical_filtered = z_coords_canonical[non_background_flags]
        depth_values_filtered = depth_values[non_background_flags]

        if depth_map_display_sparsity != 100:
            x_coords_canonical_filtered = x_coords_canonical_filtered[
                ::depth_map_display_sparsity
            ]
            y_coords_canonical_filtered = y_coords_canonical_filtered[
                ::depth_map_display_sparsity
            ]
            z_coords_canonical_filtered = z_coords_canonical_filtered[
                ::depth_map_display_sparsity
            ]
            depth_values_filtered = depth_values_filtered[
                ::depth_map_display_sparsity
            ]

        if depth_map_semantic == Camera.DEPTH_MAP_WRT_CANONICAL_VECTORS:
            # In this case, the depth values are defined w.r.t. the canonical
            # vectors. This kind of depth data is used by Colmap.
            x_coords_filtered = (
                x_coords_canonical_filtered * depth_values_filtered
            )
            y_coords_filtered = (
                y_coords_canonical_filtered * depth_values_filtered
            )
            z_coords_filtered = (
                z_coords_canonical_filtered * depth_values_filtered
            )

        elif depth_map_semantic == Camera.DEPTH_MAP_WRT_UNIT_VECTORS:
            # In this case the depth values are defined w.r.t. the normalized
            # canonical vectors. This kind of depth data is used by MVE.
            cannonical_norms_filtered = np.linalg.norm(
                np.array(
                    [
                        x_coords_canonical_filtered,
                        y_coords_canonical_filtered,
                        z_coords_canonical_filtered,
                    ],
                    dtype=float,
                ),
                axis=0,
            )
            # Instead of normalizing the x,y and z component, we divide the
            # depth values by the corresponding norm.
            normalized_depth_values_filtered = (
                depth_values_filtered / cannonical_norms_filtered
            )
            x_coords_filtered = (
                x_coords_canonical_filtered * normalized_depth_values_filtered
            )
            y_coords_filtered = (
                y_coords_canonical_filtered * normalized_depth_values_filtered
            )
            z_coords_filtered = (
                z_coords_canonical_filtered * normalized_depth_values_filtered
            )

        else:
            assert False

        cam_coords = np.dstack(
            (x_coords_filtered, y_coords_filtered, z_coords_filtered)
        )[0]

        return cam_coords
