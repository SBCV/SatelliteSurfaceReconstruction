import json

from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX
from lxml import etree

from lib.latlonalt_enu_converter import enu_to_latlonalt

# from ssr.ssr_types.python_cache import PythonCache
from ssr.file_handler.colmap_file_handler import ColmapFileHandler


# Examine the contents of
#   approx_camera /
#       affine_latlonalt.json
#       bbx_enu.json
#       bbx_latlonalt.json
#       perspective_enu.json
#       perspective_enu_error.csv


def compute_kml_point_description(coord, name):
    coords_str = " " + ",".join(str(num) for num in coord) + " "
    description = KML.Placemark(
        KML.name(name),
        KML.Point(
            # https://developers.google.com/kml/documentation/altitudemode
            # possible values:
            #   from the surface of the Earth(relativeToGround)
            #   above sea level(absolute)
            #   from the bottom of major bodies of water (relativeToSeaFloor)
            GX.altitudeMode("absolute"),
            KML.coordinates(coords_str),
        ),
    )
    return description


def compute_kml_line_3d_description(coord_list, name):

    coord_str_list = [" "]
    for coord in coord_list:
        coords_str = ",".join(str(num) for num in coord) + " "
        coord_str_list.append(coords_str)

    description = KML.Placemark(
        KML.name(name),
        KML.LineString(
            # https://developers.google.com/kml/documentation/altitudemode
            # possible values:
            #   from the surface of the Earth(relativeToGround)
            #   above sea level(absolute)
            #   from the bottom of major bodies of water (relativeToSeaFloor)
            GX.altitudeMode("absolute"),
            KML.coordinates(*coord_str_list),
        ),
    )
    return description


def compute_kml_file_description():
    return KML.Folder(KML.name("Results"))


def write_kml_file_description(kml_description, kml_fp):
    kml_str = etree.tostring(kml_description, pretty_print=True)
    with open(kml_fp, "wb") as f:
        f.write(kml_str)


def get_observer_point(bbox_dict):
    lat0 = (bbox_dict["lat_min"] + bbox_dict["lat_max"]) / 2.0
    lon0 = (bbox_dict["lon_min"] + bbox_dict["lon_max"]) / 2.0
    alt0 = bbox_dict["alt_min"]
    return lat0, lon0, alt0


def local_to_global(bbox_dict, xx, yy, zz):

    # We adopt a simpler local Cartesian coordinate system for a specific
    # reconstruction problem. In particular, we use the East-NorthUp (ENU)
    # coordinate system, defined by first choosing an observer point
    #  (latitude0; longitude0; altitude0), and then the “east”, “north”, and
    #  “up” directions at this point form the three axes. The “east-north”
    #  plane is parallel to the tangent plane of the reference ellipsoid at
    #  the point (latitude0; longitude0; 0).
    lat0, lon0, alt0 = get_observer_point(bbox_dict)
    # ENU = East-North-Up
    xx, yy, zz = enu_to_latlonalt(xx, yy, zz, lat0, lon0, alt0).format()
    return xx, yy, zz


def compute_sfm_visualization(
    bbox_json_ifp, colmap_model_idp, kml_ofp, add_image_names=True
):
    """
    bbox_json_ifp points to a file containing something similar to:

    {
      "lat_min": -34.49307826776086,
      "lat_max": -34.48682494418016,
      "lon_min": -58.58976930988413,
      "lon_max": -58.58154182672741,
      "alt_min": -20.0,
      "alt_max": 100.0
    }
    """

    # cache = PythonCache()
    # cameras, _ = cache.get_cached_result(
    #     callback=ColmapFileHandler.parse_colmap_model_folder,
    #     params=[colmap_model_idp, None],
    #     unique_id_or_path=1,
    # )
    cameras, _ = ColmapFileHandler.parse_colmap_model_folder(
        colmap_model_idp, None
    )

    with open(bbox_json_ifp) as bbox_json:
        bbox_dict = json.load(bbox_json)
        lat_observer, lon_observer, alt_observer = get_observer_point(
            bbox_dict
        )
        kml_file_descr = compute_kml_file_description()
        for camera in cameras:
            camera_center = camera.get_camera_center()

            east_value = camera_center[
                0
            ]  # two dimensional array (but only one dimension is used)
            north_value = camera_center[1]
            up_value = camera_center[2]
            lat_value, lon_value, alt_value = local_to_global(
                bbox_dict, east_value, north_value, up_value
            )

            # NOTE THE CHANGE OF THE ORDER (lon, lat vs lat, lon)
            coord_list = [
                [lon_value, lat_value, alt_value],
                [lon_observer, lat_observer, alt_observer],
            ]

            line_3d_description = compute_kml_line_3d_description(
                coord_list=coord_list, name=camera.file_name
            )
            kml_file_descr.append(line_3d_description)

            if add_image_names:
                # NOTE THE CHANGE OF THE ORDER (lon, lat vs lat, lon)
                point_3d_description = compute_kml_point_description(
                    coord=[lon_value, lat_value, alt_value],
                    name=camera.file_name,
                )
                kml_file_descr.append(point_3d_description)

        write_kml_file_description(kml_file_descr, kml_ofp)


if __name__ == "__main__":

    bbox_json_ifp = (
        "/path/to/MVS3D_site_1_mvs/approx_camera/bbx_latlonalt.json"
    )
    colmap_model_idp = "/path/to/MVS3D_site_1_mesh/colmap/sparse"
    kml_ofp = "/path/to/workspace/MVS3D_site_1/sfm_visualization.kml"

    compute_sfm_visualization(bbox_json_ifp, colmap_model_idp, kml_ofp)
