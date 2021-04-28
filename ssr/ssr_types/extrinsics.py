import math
import numpy as np


def quaternion_to_rotation_matrix(q):
    # Original C++ Method defined in  pba/src/pba/DataInterface.h
    qq = math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3])
    qw = qx = qy = qz = 0
    if qq > 0:  # NORMALIZE THE QUATERNION
        qw = q[0] / qq
        qx = q[1] / qq
        qy = q[2] / qq
        qz = q[3] / qq
    else:
        qw = 1
        qx = qy = qz = 0

    m = np.zeros((3, 3), dtype=float)
    m[0][0] = float(qw * qw + qx * qx - qz * qz - qy * qy)
    m[0][1] = float(2 * qx * qy - 2 * qz * qw)
    m[0][2] = float(2 * qy * qw + 2 * qz * qx)
    m[1][0] = float(2 * qx * qy + 2 * qw * qz)
    m[1][1] = float(qy * qy + qw * qw - qz * qz - qx * qx)
    m[1][2] = float(2 * qz * qy - 2 * qx * qw)
    m[2][0] = float(2 * qx * qz - 2 * qy * qw)
    m[2][1] = float(2 * qy * qz + 2 * qw * qx)
    m[2][2] = float(qz * qz + qw * qw - qy * qy - qx * qx)
    return m


def rotation_matrix_to_quaternion(m):
    # Original C++ Method defined in  pba/src/pba/DataInterface.h
    q = np.array([0, 0, 0, 0], dtype=float)
    q[0] = 1 + m[0][0] + m[1][1] + m[2][2]
    if q[0] > 0.000000001:
        q[0] = math.sqrt(q[0]) / 2.0
        q[1] = (m[2][1] - m[1][2]) / (4.0 * q[0])
        q[2] = (m[0][2] - m[2][0]) / (4.0 * q[0])
        q[3] = (m[1][0] - m[0][1]) / (4.0 * q[0])
    else:
        if m[0][0] > m[1][1] and m[0][0] > m[2][2]:
            s = 2.0 * math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2])
            q[1] = 0.25 * s
            q[2] = (m[0][1] + m[1][0]) / s
            q[3] = (m[0][2] + m[2][0]) / s
            q[0] = (m[1][2] - m[2][1]) / s

        elif m[1][1] > m[2][2]:
            s = 2.0 * math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2])
            q[1] = (m[0][1] + m[1][0]) / s
            q[2] = 0.25 * s
            q[3] = (m[1][2] + m[2][1]) / s
            q[0] = (m[0][2] - m[2][0]) / s
        else:
            s = 2.0 * math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1])
            q[1] = (m[0][2] + m[2][0]) / s
            q[2] = (m[1][2] + m[2][1]) / s
            q[3] = 0.25 * s
            q[0] = (m[0][1] - m[1][0]) / s
    return q


class Extrinsics:
    def __init__(self):

        # center is the coordinate of the camera center with respect to the
        # world coordinate frame (t = -R C)
        self._center = np.array([0, 0, 0], dtype=float)
        # the translation vector is the vector used to transform points in
        # world coordinates to camera coordinates (C = -R^T t)
        self._translation_vec = np.array([0, 0, 0], dtype=float)

        # use for these attributes the getter and setter methods
        self._quaternion = np.array([0, 0, 0, 0], dtype=float)
        # for rotations the inverse is equal to the transpose
        # self._rotation_inv_mat = np.linalg.transpose(self._rotation_mat)
        self._rotation_mat = np.zeros((3, 3), dtype=float)

    @staticmethod
    def invert_transformation_mat(trans_mat):
        # Exploit that the inverse of the rotation part is equal to the
        # transposed of the rotation part. This should be more robust than
        # trans_mat_inv = np.linalg.inv(trans_mat)
        trans_mat_inv = np.zeros_like(trans_mat)
        rotation_part_inv = trans_mat[0:3, 0:3].T
        trans_mat_inv[0:3, 0:3] = rotation_part_inv
        trans_mat_inv[0:3, 3] = -np.dot(rotation_part_inv, trans_mat[0:3, 3])
        trans_mat_inv[3, 3] = 1
        return trans_mat_inv

    def is_rotation_mat_valid(self, some_mat):
        # TEST if rotation_mat is really a rotation matrix
        # (i.e. det = -1 or det = 1)
        det = np.linalg.det(some_mat)
        is_close = np.isclose(det, 1) or np.isclose(det, -1)
        # if not is_close:
        #     logger.vinfo('some_mat', some_mat)
        #     logger.vinfo('determinante', det)
        return is_close

    def set_quaternion(self, quaternion):
        self._quaternion = quaternion
        # we must change the rotation matrixes as well
        self._rotation_mat = quaternion_to_rotation_matrix(quaternion)

    def set_rotation_mat(self, rotation_mat):
        assert self.is_rotation_mat_valid(rotation_mat)
        self._rotation_mat = rotation_mat
        # we must change the quaternion as well
        self._quaternion = rotation_matrix_to_quaternion(rotation_mat)

    def set_camera_center_after_rotation(self, center):
        assert self.is_rotation_mat_valid(self._rotation_mat)
        self._center = center
        self._translation_vec = -np.dot(self._rotation_mat, center)

    def set_camera_translation_vector_after_rotation(self, translation_vector):
        # translation_vector: trans_vec = -Rc

        assert self.is_rotation_mat_valid(self._rotation_mat)
        self._translation_vec = translation_vector
        self._center = -np.dot(
            self._rotation_mat.transpose(), translation_vector
        )

    def get_quaternion(self):
        return self._quaternion

    def get_rotation_mat(self):
        # Note:
        # self._rotation_mat.T or self._rotation_mat.transpose()
        # DO NOT CHANGE THE MATRIX
        return self._rotation_mat

    def get_translation_vec(self):
        return self._translation_vec

    def get_camera_center(self):
        return self._center

    def get_4x4_world_to_cam_mat(self):
        # This matrix can be used to convert points given in world coordinates
        # into points given in camera coordinates
        # M = [R      -Rc]
        #     [0      1],
        # https://en.wikipedia.org/wiki/Transformation_matrix#/media/File:2D_affine_transformation_matrix.svg

        homogeneous_mat = np.identity(4, dtype=float)
        homogeneous_mat[0:3, 0:3] = self.get_rotation_mat()
        homogeneous_mat[0:3, 3] = -self.get_rotation_mat().dot(
            self.get_camera_center()
        )
        return homogeneous_mat

    def set_4x4_cam_to_world_mat(self, cam_to_world_mat):
        # This matrix can be used to convert points given in camera coordinates
        # into points given in world coordinates
        # M = [R^T    c]
        #     [0      1]
        #
        # https://en.wikipedia.org/wiki/Transformation_matrix#/media/File:2D_affine_transformation_matrix.svg

        rotation_part = cam_to_world_mat[0:3, 0:3]
        translation_part = cam_to_world_mat[0:3, 3]
        self.set_rotation_mat(rotation_part.transpose())
        self.set_camera_center_after_rotation(translation_part)

    def get_4x4_cam_to_world_mat(self):
        # This matrix can be used to convert points given in camera coordinates
        # into points given in world coordinates
        # M = [R^T    c]
        #     [0      1]
        # :return:
        #
        # https://en.wikipedia.org/wiki/Transformation_matrix#/media/File:2D_affine_transformation_matrix.svg

        homogeneous_mat = np.identity(4, dtype=float)
        homogeneous_mat[0:3, 0:3] = self.get_rotation_mat().transpose()
        homogeneous_mat[0:3, 3] = self.get_camera_center()
        return homogeneous_mat

    def cam_to_world_coord_multiple_coords(self, cam_coords):

        num_coords = cam_coords.shape[0]
        hom_entries = np.ones(num_coords).reshape((num_coords, 1))
        cam_coords_hom = np.hstack((cam_coords, hom_entries))
        world_coords_hom = (
            self.get_4x4_cam_to_world_mat().dot(cam_coords_hom.T).T
        )
        world_coords = np.delete(world_coords_hom, 3, 1)
        return world_coords
