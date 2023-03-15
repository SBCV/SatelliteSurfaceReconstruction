import numpy as np
from collections import defaultdict
from pprint import pformat


class Measurement:
    def __init__(self, camera_index, feature_index, x, y, x_y_are_image_coords=None):
        self.camera_index = int(camera_index)
        self.feature_index = int(feature_index)
        # Measurement positions are expressed in "computer vision coordinates"
        # i.e. they start in the upper left of an image
        self.x = x
        self.y = y
        # Colmap and OpenMVG use [0, width] x [0, height]
        # VisualSfM uses [-width/2, width/2] x [-height/2, height/2]
        # If has_image_coords=True, x and y are within [0, width] x [0, height]
        # If has_image_coords=False, x and y are within
        # [-width/2, width/2] x [-height/2, height/2]
        self.x_y_are_image_coords = x_y_are_image_coords

    @classmethod
    def init_from_list(cls, arr):
        return cls(int(arr[0]), int(arr[1]), arr[2], arr[3])

    def __str__(self):
        return (
            str(self.camera_index)
            + " "
            + str(self.feature_index)
            + " "
            + str(self.x)
            + " "
            + str(self.y)
        )

    def __repr__(self):
        return self.__str__()

    def get_x_y(self):
        return self.x, self.y

    def to_numpy_array(self):
        return np.array(self.camera_index, self.feature_index, self.x, self.y)

    def to_list(self):
        return [self.camera_index, self.feature_index, self.x, self.y]


class Point:
    def __init__(
        self,
        coord=np.array([0, 0, 0], dtype=float),
        color=np.array([255, 255, 255], dtype=int),
        measurements=None,
    ):

        self.coord = np.asarray(coord, dtype=float)
        self.color = np.asarray(color, dtype=int)

        self.with_normal = False
        self.normal = np.array([0, 0, 0], dtype=float)

        # Measurements is a list of < Measurement >
        # < Measurement > = < Image index > < Feature Index > < xy >
        self.measurements = measurements
        self.is_object_point = None

        self.id = None

        # self.point.scalars[scalar_key] = scalar_value
        self.scalars = defaultdict(lambda: None)

    def set_coord(self, coord):
        self.coord = np.asarray(coord, dtype=float)

    def set_color(self, color):
        self.color = np.asarray(color, dtype=int)

    def set_normal(self, normal):
        self.normal = np.asarray(normal, dtype=float)
        self.with_normal = True

    def get_coord_as_array(self):
        return np.asarray(self.coord, dtype=float)

    def get_color_as_array(self):
        return np.asarray(self.coord, dtype=int)

    def get_normal_as_array(self):
        return np.asarray(self.coord, dtype=float)

    def get_hom_coord_as_array(self):
        return np.append(self.coord, [1])

    def __repr__(self):
        # __repr__ is called for example when printing lists of Points
        return self.__str__()

    def __str__(self):
        prop_str = pformat(
            vars(self)
        )  # returns a dictionary of attribute names with values
        return prop_str

    # defines how the class will be compared
    def __lt__(self, other):
        return self.coord < other.coord

    def __add__(self, other):
        return Point(
            coord=self.coord + other.coord,
            color=(self.color + other.color) / 2,
        )

    def __radd__(self, other):
        return Point(
            coord=self.coord + other.coord,
            color=(self.color + other.color) / 2,
        )

    def __sub__(self, other):
        return Point(
            coord=self.coord - other.coord,
            color=(self.color + other.color) / 2,
        )

    def __rsub__(self, other):
        return Point(
            coord=self.coord - other.coord,
            color=(self.color + other.color) / 2,
        )

    def __mul__(self, scalar):
        return Point(coord=self.coord * scalar, color=self.color)

    def __rmul__(self, scalar):
        return Point(coord=self.coord * scalar, color=self.color)

    @classmethod
    def get_points_from_coords(cls, coords):
        points = []
        for id, coord in enumerate(coords):
            point = cls(coord)
            point.id = id
            points.append(point)
        return points

    @staticmethod
    def get_coords_from_points(points):
        return [point.get_coord_as_array() for point in points]
