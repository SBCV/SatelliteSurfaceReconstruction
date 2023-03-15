import os
import numpy as np
from ssr.ext.read_write_model import (
    read_model,
    read_cameras_text,
    read_cameras_binary,
    read_images_text,
    read_images_binary,
    write_model,
    write_cameras_text,
    write_cameras_binary,
)
from ssr.ext.read_write_model import Camera as ColmapCamera
from ssr.ext.read_write_model import Image as ColmapImage
from ssr.ext.read_write_model import Point3D as ColmapPoint3D

from ssr.ssr_types.camera import Camera
from ssr.ssr_types.point import Point

from ssr.utility.logging_extension import logger

# From ssr\ext\read_write_model.py
# CAMERA_MODELS = {
#     CameraModel(model_id=0, model_name="SIMPLE_PINHOLE", num_params=3),
#     CameraModel(model_id=1, model_name="PINHOLE", num_params=4),
#     CameraModel(model_id=2, model_name="SIMPLE_RADIAL", num_params=4),
#     CameraModel(model_id=3, model_name="RADIAL", num_params=5),
#     CameraModel(model_id=4, model_name="OPENCV", num_params=8),
#     CameraModel(model_id=5, model_name="OPENCV_FISHEYE", num_params=8),
#     CameraModel(model_id=6, model_name="FULL_OPENCV", num_params=12),
#     CameraModel(model_id=7, model_name="FOV", num_params=5),
#     CameraModel(model_id=8, model_name="SIMPLE_RADIAL_FISHEYE", num_params=4),
#     CameraModel(model_id=9, model_name="RADIAL_FISHEYE", num_params=5),
#     CameraModel(model_id=10, model_name="THIN_PRISM_FISHEYE", num_params=12)
# }

# From https://github.com/colmap/colmap/blob/dev/src/base/camera_models.h
#   SIMPLE_PINHOLE: f, cx, cy
#   PINHOLE: fx, fy, cx, cy
#   SIMPLE_RADIAL: f, cx, cy, k
#   RADIAL: f, cx, cy, k1, k2
#   OPENCV: fx, fy, cx, cy, k1, k2, p1, p2
#   OPENCV_FISHEYE: fx, fy, cx, cy, k1, k2, k3, k4
#   FULL_OPENCV: fx, fy, cx, cy, k1, k2, p1, p2, k3, k4, k5, k6
#   FOV: fx, fy, cx, cy, omega
#   SIMPLE_RADIAL_FISHEYE: f, cx, cy, k
#   RADIAL_FISHEYE: f, cx, cy, k1, k2
#   THIN_PRISM_FISHEYE: fx, fy, cx, cy, k1, k2, p1, p2, k3, k4, sx1, sy1


def parse_camera_param_list(colmap_cam):
    name = colmap_cam.model
    params = colmap_cam.params
    return decompose_params(name, params)


def decompose_params(camera_model_name, params):
    fx, fy, cx, cy, skew = None, None, None, None, None
    r1, r2 = None, None
    if camera_model_name == "SIMPLE_PINHOLE":
        fx, cx, cy = params
    elif camera_model_name == "PINHOLE":
        fx, fy, cx, cy = params
    elif camera_model_name == "SIMPLE_RADIAL":
        fx, cx, cy, r1 = params
    elif camera_model_name == "RADIAL":
        fx, cx, cy, _, _ = params
    elif camera_model_name == "OPENCV":
        fx, fy, cx, cy, _, _, _, _ = params
    elif camera_model_name == "OPENCV_FISHEYE":
        fx, fy, cx, cy, _, _, _, _ = params
    elif camera_model_name == "FULL_OPENCV":
        fx, fy, cx, cy, _, _, _, _, _, _, _, _ = params
    elif camera_model_name == "FOV":
        fx, fy, cx, cy, _ = params
    elif camera_model_name == "SIMPLE_RADIAL_FISHEYE":
        fx, cx, cy, _ = params
    elif camera_model_name == "RADIAL_FISHEYE":
        fx, cx, cy, _, _ = params
    elif camera_model_name == "THIN_PRISM_FISHEYE":
        fx, fy, cx, cy, _, _, _, _, _, _, _, _ = params
    elif camera_model_name == "PERSPECTIVE":
        fx, fy, cx, cy, skew = params
    if fy is None:
        fy = fx
    if skew is None:
        skew = 0.0
    return fx, fy, cx, cy, skew


def create_camera_param_list(custom_cam, camera_model_name):
    calib_mat = custom_cam.get_calibration_mat()
    return compose_params(camera_model_name, calib_mat)


def compose_params(camera_model_name, calib_mat):

    fx = calib_mat[0][0]
    skew = calib_mat[0][1]
    cx = calib_mat[0][2]

    fy = calib_mat[1][1]
    cy = calib_mat[1][2]

    if camera_model_name == "SIMPLE_PINHOLE":
        assert fx == fy
        assert skew == 0
        params = fx, cx, cy
    elif camera_model_name == "PINHOLE":
        params = fx, fy, cx, cy
    elif camera_model_name == "PERSPECTIVE":
        params = fx, fy, cx, cy, skew
    else:
        assert False

    return params


class ColmapFileHandler(object):
    @staticmethod
    def convert_colmap_cams_to_cams(id_to_col_cameras, id_to_col_images, image_dp):
        # From ssr\ext\read_write_model.py
        #   CameraModel = collections.namedtuple(
        #       "CameraModel", ["model_id", "model_name", "num_params"])
        #   Camera = collections.namedtuple(
        #       "Camera", ["id", "model", "width", "height", "params"])
        #   BaseImage = collections.namedtuple(
        #       "Image", ["id", "qvec", "tvec", "camera_id", "name", "xys", "point3D_ids"])

        cameras = []
        for col_image in id_to_col_images.values():
            current_camera = Camera()
            current_camera.id = col_image.id
            current_camera.set_quaternion(col_image.qvec)
            current_camera.set_camera_translation_vector_after_rotation(col_image.tvec)

            current_camera.image_dp = image_dp
            current_camera.file_name = col_image.name

            camera_model = id_to_col_cameras[col_image.camera_id]
            current_camera.width = camera_model.width
            current_camera.height = camera_model.height

            fx, fy, cx, cy, skew = parse_camera_param_list(camera_model)
            camera_calibration_matrix = np.array(
                [[fx, skew, cx], [0, fy, cy], [0, 0, 1]]
            )
            current_camera.set_calibration(
                camera_calibration_matrix, radial_distortion=0
            )
            cameras.append(current_camera)

        return cameras

    @staticmethod
    def convert_colmap_points_to_points(id_to_col_points3D):
        # From ssr\ext\read_write_model.py
        #   Point3D = collections.namedtuple(
        #       "Point3D", ["id", "xyz", "rgb", "error", "image_ids", "point2D_idxs"])

        col_points3D = id_to_col_points3D.values()
        points3D = []
        for col_point3D in col_points3D:
            current_point = Point(coord=col_point3D.xyz, color=col_point3D.rgb)
            current_point.id = col_point3D.id
            points3D.append(current_point)

        return points3D

    @staticmethod
    def parse_colmap_model_folder(model_idp, image_idp):

        logger.info("Parse Colmap model folder: " + model_idp)

        ifp_s = os.listdir(model_idp)

        if (
            len(set(ifp_s).intersection(["cameras.txt", "images.txt", "points3D.txt"]))
            == 3
        ):
            ext = ".txt"
        elif (
            len(set(ifp_s).intersection(["cameras.bin", "images.bin", "points3D.bin"]))
            == 3
        ):
            ext = ".bin"
        else:
            assert False  # No valid model folder

        # Cameras represent information about the camera model.
        # Images contain pose information.
        id_to_col_cameras, id_to_col_images, id_to_col_points3D = read_model(
            model_idp, ext=ext
        )
        cameras = ColmapFileHandler.convert_colmap_cams_to_cams(
            id_to_col_cameras, id_to_col_images, image_idp
        )
        points3D = ColmapFileHandler.convert_colmap_points_to_points(id_to_col_points3D)

        return cameras, points3D

    @staticmethod
    def parse_colmap_cams(model_idp, image_dp):

        ifp_s = os.listdir(model_idp)

        if len(set(ifp_s).intersection(["cameras.txt", "images.txt"])) == 2:
            ext = ".txt"
        elif len(set(ifp_s).intersection(["cameras.bin", "images.bin"])) == 2:
            ext = ".bin"
        else:
            assert False  # No valid model folder

        if ext == ".txt":
            id_to_col_cameras = read_cameras_text(
                os.path.join(model_idp, "cameras" + ext)
            )
            id_to_col_images = read_images_text(os.path.join(model_idp, "images" + ext))

        elif ext == ".bin":
            id_to_col_cameras = read_cameras_binary(
                os.path.join(model_idp, "cameras" + ext)
            )
            id_to_col_images = read_images_binary(
                os.path.join(model_idp, "images" + ext)
            )
        else:
            assert False

        cameras = ColmapFileHandler.convert_colmap_cams_to_cams(
            id_to_col_cameras, id_to_col_images, image_dp
        )

        return cameras

    @staticmethod
    def convert_cams_to_colmap_cams_and_colmap_images(
        cameras, colmap_camera_model_name="SIMPLE_PINHOLE"
    ):
        colmap_cams = {}
        colmap_images = {}
        for cam in cameras:

            cam.get_calibration_mat()
            param_list = create_camera_param_list(cam, colmap_camera_model_name)

            colmap_cam = ColmapCamera(
                id=cam.id,
                model=colmap_camera_model_name,
                width=cam.width,
                height=cam.height,
                params=np.asarray(param_list),
            )
            colmap_cams[cam.id] = colmap_cam

            colmap_image = ColmapImage(
                id=cam.id,
                qvec=cam.get_quaternion(),
                tvec=cam.get_translation_vec(),
                camera_id=cam.id,
                name=cam.get_file_name(),
                xys=[],
                point3D_ids=[],
            )
            colmap_images[cam.id] = colmap_image

        return colmap_cams, colmap_images

    @staticmethod
    def convert_points_to_colmap_points(points):
        colmap_points3D = {}
        for point in points:
            colmap_point = ColmapPoint3D(
                id=point.id,
                xyz=point.coord,
                rgb=point.color,
                error=0,
                # The default settings in Colmap show only points with 3+ observations
                image_ids=[0, 1, 2],
                point2D_idxs=[0, 1, 2],
            )
            colmap_points3D[point.id] = colmap_point
        return colmap_points3D

    @staticmethod
    def write_colmap_model(
        odp, cameras, points, colmap_camera_model_name="SIMPLE_PINHOLE"
    ):
        logger.info("Write Colmap model folder: " + odp)

        if not os.path.isdir(odp):
            os.mkdir(odp)

        # From ssr\ext\read_write_model.py
        #   CameraModel = collections.namedtuple(
        #       "CameraModel", ["model_id", "model_name", "num_params"])
        #   Camera = collections.namedtuple(
        #       "Camera", ["id", "model", "width", "height", "params"])
        #   BaseImage = collections.namedtuple(
        #       "Image", ["id", "qvec", "tvec", "camera_id", "name", "xys", "point3D_ids"])
        #   Point3D = collections.namedtuple(
        #       "Point3D", ["id", "xyz", "rgb", "error", "image_ids", "point2D_idxs"])

        (
            colmap_cams,
            colmap_images,
        ) = ColmapFileHandler.convert_cams_to_colmap_cams_and_colmap_images(
            cameras, colmap_camera_model_name
        )

        colmap_points3D = ColmapFileHandler.convert_points_to_colmap_points(points)

        write_model(colmap_cams, colmap_images, colmap_points3D, odp, ext=".txt")

    @staticmethod
    def write_colmap_cameras(
        odp, cameras, colmap_camera_model_name="SIMPLE_PINHOLE", ext=".txt"
    ):

        (
            colmap_cams,
            _,
        ) = ColmapFileHandler.convert_cams_to_colmap_cams_and_colmap_images(
            cameras, colmap_camera_model_name
        )

        if ext == ".txt":
            write_cameras_text(colmap_cams, os.path.join(odp, "cameras" + ext))
        elif ext == ".bin":
            write_cameras_binary(colmap_cams, os.path.join(odp, "cameras" + ext))
