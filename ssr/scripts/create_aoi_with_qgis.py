import geojson
import json
import numpy as np
import pyproj
import utm
from ssr.utility.logging_extension import logger


def latlon_to_utm(lat, lon):

    # For conversion between (lat, lon) and (utm east, utm north), please
    # refer to: lib/latlon_utm_converter.py
    #   https://github.com/Kai-46/VisSatSatelliteStereo/blob/master/lib/latlon_utm_converter.py

    lat_arr = np.array([lat]).reshape((1, 1))
    lon_arr = np.array([lon]).reshape((1, 1))
    # assume all the points are either on north or south hemisphere
    assert np.all(lat_arr >= 0) or np.all(lat_arr < 0)
    if lat_arr[0, 0] >= 0:  # north hemisphere
        south = False
    else:
        south = True
    _, _, zone_number, _ = utm.from_latlon(lat_arr[0, 0], lon_arr[0, 0])
    proj = pyproj.Proj(
        proj="utm", ellps="WGS84", zone=zone_number, south=south
    )
    east_arr, north_arr = proj(lon_arr, lat_arr)
    if south:
        hemisphere = "S"
    else:
        hemisphere = "N"
    east = east_arr[0][0]
    north = north_arr[0][0]
    return east, north, zone_number, hemisphere


def utm_to_latlon(east, north, zone_number, hemisphere):

    # For conversion between (lat, lon) and (utm east, utm north), please
    # refer to: lib/latlon_utm_converter.py
    #   https://github.com/Kai-46/VisSatSatelliteStereo/blob/master/lib/latlon_utm_converter.py

    south = hemisphere != "N"
    east_arr = np.array([east]).reshape((1, 1))
    north_arr = np.array([north]).reshape((1, 1))
    proj = pyproj.Proj(
        proj="utm", ellps="WGS84", zone=zone_number, south=south
    )
    lon_arr, lat_arr = proj(east_arr, north_arr, inverse=True)
    lon = lon_arr[0][0]
    lat = lat_arr[0][0]
    return lat, lon


def convert_vissat_config_json_to_geojson(vissat_config_json_ifp, geojson_ofp):

    with open(vissat_config_json_ifp) as json_file:
        vissat_config_json = json.load(json_file)

    bbx_utm = vissat_config_json["bounding_box"]
    zone_number = bbx_utm["zone_number"]
    hemisphere = bbx_utm["hemisphere"]
    ul_easting = bbx_utm["ul_easting"]
    ul_northing = bbx_utm["ul_northing"]

    logger.info(
        "utm: {}".format(([ul_easting, ul_northing, zone_number, hemisphere]))
    )

    # See write_aoi() in stereo_pipeline.py
    lr_easting = ul_easting + bbx_utm["width"]
    lr_northing = ul_northing - bbx_utm["height"]

    # compute a lat_lon bbx
    corners_easting = [ul_easting, lr_easting, lr_easting, ul_easting]
    corners_northing = [ul_northing, ul_northing, lr_northing, lr_northing]
    corners_lat = []
    corners_lon = []
    northern = True if hemisphere == "N" else False
    for i in range(4):
        lat, lon = utm.to_latlon(
            corners_easting[i],
            corners_northing[i],
            zone_number,
            northern=northern,
        )
        corners_lat.append(lat)
        corners_lon.append(lon)
    lat_min = min(corners_lat)
    lat_max = max(corners_lat)
    lon_min = min(corners_lon)
    lon_max = max(corners_lon)

    lat, lon = utm_to_latlon(ul_easting, ul_northing, zone_number, hemisphere)
    logger.info("lat lon: {}".format([lat, lon]))

    vertex_list = [
        (lon_min, lat_min),
        (lon_min, lat_max),
        (lon_max, lat_max),
        (lon_max, lat_min),
    ]

    # A LineString only marks the border of the area (but is not a closed
    # shape, i.e. no loop).
    # my_linestring = geojson.LineString(vertex_list)
    # geojson_str = geojson.dumps(my_linestring, sort_keys=True)

    # A polygon is filled by default in QGIS (style can be changed in the
    # raster layer properties)
    my_polygon = geojson.Polygon([vertex_list])
    geojson_str = geojson.dumps(my_polygon, sort_keys=True)

    with open(geojson_ofp, "w") as geojson_file:
        geojson_file.write(geojson_str)


def create_vissat_json_config(
    dataset_dir="",
    work_dir="",
    zone_number=0,
    hemisphere="",
    ul_easting="",
    ul_northing="",
    width=0,
    height=0,
    alt_min=-30,
    alt_max=120,
):

    vissat_dict = {}
    vissat_dict["dataset_dir"] = dataset_dir
    vissat_dict["work_dir"] = work_dir
    vissat_dict["bounding_box"] = {}
    vissat_dict["bounding_box"]["zone_number"] = zone_number
    vissat_dict["bounding_box"]["hemisphere"] = hemisphere
    vissat_dict["bounding_box"]["ul_easting"] = ul_easting
    vissat_dict["bounding_box"]["ul_northing"] = ul_northing
    vissat_dict["bounding_box"]["width"] = width
    vissat_dict["bounding_box"]["height"] = height
    vissat_dict["steps_to_run"] = {}
    vissat_dict["steps_to_run"]["clean_data"] = True
    vissat_dict["steps_to_run"]["crop_image"] = True
    vissat_dict["steps_to_run"]["derive_approx"] = True
    vissat_dict["steps_to_run"]["choose_subset"] = True
    vissat_dict["steps_to_run"]["colmap_sfm_perspective"] = True
    vissat_dict["steps_to_run"]["inspect_sfm_perspective"] = True
    vissat_dict["steps_to_run"]["reparam_depth"] = True
    vissat_dict["steps_to_run"]["colmap_mvs"] = True
    vissat_dict["steps_to_run"]["aggregate_2p5d"] = True
    vissat_dict["steps_to_run"]["aggregate_3d"] = True
    vissat_dict["alt_min"] = alt_min
    vissat_dict["alt_max"] = alt_max
    return vissat_dict


def convert_geojson_to_vissat_config_json(geojson_ifp, vissat_config_json_ofp):

    """
    geojson_ifp must contain something like the following:

    {
    "type": "FeatureCollection",
    "name": "custom",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
    "features": [
    { "type": "Feature", "properties": { }, "geometry": { "type": "Polygon", "coordinates": [ [ [ -58.585334076016956, -34.483021854247148 ], [ -58.592695017702304, -34.482823108615037 ], [ -58.592723383566216, -34.478169987332244 ], [ -58.585220612561308, -34.478357052491198 ], [ -58.585334076016956, -34.483021854247148 ] ] ] } }
    ]
    }
    """

    with open(geojson_ifp) as geojson_file:
        vissat_config_json = json.load(geojson_file)

    geometry = vissat_config_json["features"][0]["geometry"]

    if geometry["type"] == "MultiPolygon":
        vertex_list = geometry["coordinates"][0][0]
    elif geometry["type"] == "Polygon":
        vertex_list = geometry["coordinates"][0]
    else:
        assert False

    # compute bounding box
    lon_list = [vertex[0] for vertex in vertex_list]
    lat_list = [vertex[1] for vertex in vertex_list]

    lat_min = min(lat_list)
    lat_max = max(lat_list)
    lon_min = min(lon_list)
    lon_max = max(lon_list)

    east_min, north_min, zone_number, hemisphere = latlon_to_utm(
        lat_min, lon_min
    )

    east_max, north_max, zone_number, hemisphere = latlon_to_utm(
        lat_max, lon_max
    )
    width = east_max - east_min
    height = north_max - north_min

    vissat_dict = create_vissat_json_config(
        dataset_dir="",
        work_dir="",
        zone_number=zone_number,
        hemisphere=hemisphere,
        ul_easting=east_min,
        ul_northing=north_max,
        width=width,
        height=height,
        alt_min=-30,
        alt_max=120,
    )

    with open(vissat_config_json_ofp, "w") as vissat_config_json_file:
        vissat_config_json_file.write(json.dumps(vissat_dict))


if __name__ == "__main__":

    # For conversion between (lat, lon, alt) and local ENU, please refer to
    # coordinate_system.py and latlonalt_enu_converter.py:
    #   https://github.com/Kai-46/VisSatSatelliteStereo/blob/master/coordinate_system.py
    #   https://github.com/Kai-46/VisSatSatelliteStereo/blob/master/lib/latlonalt_enu_converter.py

    custom_geojson_ifp = "/path/to/custom.geojson"
    custom_vissat_json_ofp = "/path/to/custom_vissat.json"
    custom_bbox_geojson_ofp = "/path/to/custom_bbox.geojson"

    convert_geojson_to_vissat_config_json(
        custom_geojson_ifp, custom_vissat_json_ofp
    )
    convert_vissat_config_json_to_geojson(
        custom_vissat_json_ofp, custom_bbox_geojson_ofp
    )
