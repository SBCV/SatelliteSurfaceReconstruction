import numpy as np
import math
from ssr.utility.logging_extension import logger


class Intrinsics:
    def __init__(self):
        # contains focal length and pivot point, but NO distortion parameters
        self._calibration_mat1 = np.zeros((3, 3), dtype=float)
        # Only radial distortion with 1 distortion parameter is supported
        self._radial_distortion = None

    def set_calibration(self, calibration_mat, radial_distortion):
        self._calibration_mat1 = np.asarray(calibration_mat, dtype=float)
        self._radial_distortion = float(radial_distortion)
        assert self._radial_distortion is not None

    def check_calibration_mat(self):
        assert self.is_principal_point_initialized()

    def get_calibration_mat(self):
        self.check_calibration_mat()
        return self._calibration_mat1

    def set_principal_point(self, principal_point):
        self._calibration_mat1[0][2] = principal_point[0]
        self._calibration_mat1[1][2] = principal_point[1]

    def get_principal_point(self):
        calibration_mat = self.get_calibration_mat()
        cx = calibration_mat[0][2]
        cy = calibration_mat[1][2]
        return np.asarray([cx, cy], dtype=float)

    def is_principal_point_initialized(self):
        cx_zero = np.isclose(self._calibration_mat1[0][2], 0.0)
        cy_zero = np.isclose(self._calibration_mat1[1][2], 0.0)
        initialized = (not cx_zero) and (not cy_zero)
        return initialized

    # def set_height(self, height):
    #     self.height = height
    #
    # def get_height(self):
    #     assert self.height > 0     # height not properly initialized
    #     return self.height
    #
    # def set_width(self, width):
    #     self.width = width
    #
    # def get_width(self):
    #     assert self.width > 0      # width not properly initialized
    #     return self.width

    @staticmethod
    def compute_calibration_mat(focal_length, cx, cy):
        return np.array(
            [[focal_length, 0, cx], [0, focal_length, cy], [0, 0, 1]],
            dtype=float,
        )

    def get_focal_length(self):
        assert self._calibration_mat1[0][0] == self._calibration_mat1[1][1]
        return self._calibration_mat1[0][0]

    def get_fx(self):
        return self._calibration_mat1[0][0]

    def get_fy(self):
        return self._calibration_mat1[1][1]

    @staticmethod
    def compute_view_angle(focal_length, width, height):
        min_extend = min(width, height)
        angle_of_view = 2 * math.degrees(
            math.atan((min_extend / float(2.0 * focal_length)))
        )
        return angle_of_view

    def get_view_angle(self):
        assert self.width is not None and self.width > 0
        assert self.height is not None and self.height > 0
        focal_length = self.get_focal_length()
        angle_of_view = Intrinsics.compute_view_angle(
            focal_length, self.width, self.height
        )
        return angle_of_view

    def get_radial_distortion(self):
        assert self._radial_distortion is not None
        return self._radial_distortion

    def has_radial_distortion(self):
        return (
            self._radial_distortion is not None
            and self._radial_distortion != 0.0
        )

    @staticmethod
    def split_intrinsic_mat(intrinsic_mat):
        f_x = intrinsic_mat[0][0]
        f_y = intrinsic_mat[1][1]
        skew = intrinsic_mat[0][1]
        p_x = intrinsic_mat[0][2]
        p_y = intrinsic_mat[1][2]
        return f_x, f_y, skew, p_x, p_y

    @staticmethod
    def compute_intrinsic_skew_decomposition(intrinsic_mat):

        f_x, f_y, skew, p_x, p_y = Intrinsics.split_intrinsic_mat(
            intrinsic_mat
        )
        intrinsic_mat_wo_skew = np.array(
            [[f_x, 0, p_x - skew * p_y / f_y], [0, f_y, p_y], [0, 0, 1]],
            dtype=float,
        )
        skew_mat = np.array(
            [[1, skew / f_y, 0], [0, 1, 0], [0, 0, 1]], dtype=float
        )
        if not np.allclose(intrinsic_mat, skew_mat @ intrinsic_mat_wo_skew):
            err_mat = intrinsic_mat - skew_mat @ intrinsic_mat_wo_skew
            logger.vinfo("err_mat\n", err_mat)
            assert False

        return skew_mat, intrinsic_mat_wo_skew

    @staticmethod
    def compute_intrinsic_transformation(
        intrinsic_1, intrinsic_2, check_result=True
    ):
        f_x, f_y, s, p_x, p_y = Intrinsics.split_intrinsic_mat(intrinsic_1)
        f_x_, f_y_, s_, p_x_, p_y_ = Intrinsics.split_intrinsic_mat(
            intrinsic_2
        )
        trans_mat_2_to_1 = np.asarray(
            [
                [
                    f_x / f_x_,
                    -f_x * s_ / (f_x_ * f_y_) + s / f_y_,
                    f_x * p_y_ * s_ / (f_x_ * f_y_)
                    - f_x * p_x_ / f_x_
                    - p_y_ * s / f_y_
                    + p_x,
                ],
                [0, f_y / f_y_, -f_y * p_y_ / f_y_ + p_y],
                [0, 0, 1],
            ],
            dtype=np.float32,
        )

        if check_result:
            intrinsic_1_restored = trans_mat_2_to_1 @ intrinsic_2
            assert np.allclose(intrinsic_1, intrinsic_1_restored)

        return trans_mat_2_to_1


if __name__ == "__main__":

    f_x = 2800
    f_y = 2100
    s = 0.3
    p_x = 2355
    p_y = 2500

    f_x_ = 2200
    f_y_ = 2400
    s_ = 0.1
    p_x_ = 1600
    p_y_ = 800

    intrinsic_1 = np.array(
        [[f_x, s, p_x], [0, f_y, p_y], [0, 0, 1]], dtype=float
    )

    intrinsic_2 = np.array(
        [[f_x_, s_, p_x_], [0, f_y_, p_y_], [0, 0, 1]], dtype=float
    )

    trans_mat_2_to_1 = Intrinsics.compute_intrinsic_transformation(
        intrinsic_1, intrinsic_2, check_result=True
    )
    intrinsic_1_restored = trans_mat_2_to_1 @ intrinsic_2

    logger.vinfo("trans_mat_2_to_1", trans_mat_2_to_1)
    logger.vinfo("intrinsic_1", intrinsic_1)
    logger.vinfo("intrinsic_1_restored", intrinsic_1_restored)
