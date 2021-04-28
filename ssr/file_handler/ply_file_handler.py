import numpy as np
from ssr.ext.plyfile import PlyData, PlyElement
from ssr.utility.logging_extension import logger
from ssr.types.point import Point, Measurement


class Face:
    # Do NOT confuse this class with a real triangle.
    # A face saves ONLY VERTEX INDICES, NO 3D information.

    def __init__(self, initial_indices=np.array([-1, -1, -1], dtype=int)):
        # We do NOT DEFINE COLOR PER FACE, since the color of the face is
        # determined by the corresponding vertex colors
        self.vertex_indices = np.array(initial_indices, dtype=int)

    def __str__(self):
        return str(self.vertex_indices)


class PLYFileHandler:
    @staticmethod
    def __ply_data_vertices_to_vetex_list(ply_data):

        vertex_data_type_names = ply_data["vertex"].data.dtype.names
        use_color = False
        if (
            "red" in vertex_data_type_names
            and "green" in vertex_data_type_names
            and "blue" in vertex_data_type_names
        ):
            use_color = True

        vertices = []
        value_keys = [
            x
            for x, y in sorted(
                ply_data["vertex"].data.dtype.fields.items(),
                key=lambda k: k[1],
            )
        ]
        non_scalar_value_keys = [
            "x",
            "y",
            "z",
            "red",
            "green",
            "blue",
            "nx",
            "ny",
            "nz",
            "measurements",
        ]
        scalar_value_keys = [
            value_key
            for value_key in value_keys
            if not value_key in non_scalar_value_keys
        ]
        logger.info(
            "Found the following vertex properties: " + str(value_keys)
        )

        logger.info("Found " + str(len(ply_data["vertex"].data)) + " vertices")
        for point_index, line in enumerate(ply_data["vertex"].data):
            current_point = Point()
            current_point.coord = np.array([line["x"], line["y"], line["z"]])
            if use_color:
                current_point.color = np.array(
                    [line["red"], line["green"], line["blue"]]
                )
            current_point.id = point_index

            for scalar_value_key in scalar_value_keys:
                current_point.scalars[scalar_value_key] = line[
                    scalar_value_key
                ]

            if "measurements" in line.dtype.names:
                elements_per_measurement = 4
                current_point.measurements = []
                for measurement_idx in range(
                    len(line["measurements"]) / elements_per_measurement
                ):
                    array_idx = measurement_idx * elements_per_measurement
                    slice = line["measurements"][
                        array_idx : array_idx + elements_per_measurement
                    ]
                    current_point.measurements.append(
                        Measurement.init_from_list(slice)
                    )

            vertices.append(current_point)

        ply_data_vertex_dtype = ply_data["vertex"].dtype
        ply_data_vertex_data_dtype = ply_data["vertex"].data.dtype

        return vertices, ply_data_vertex_dtype, ply_data_vertex_data_dtype

    @staticmethod
    def __ply_data_faces_to_face_list(ply_data):
        faces = []
        ply_data_face_type = None
        ply_data_face_data_type = None
        if "face" in ply_data:
            # read faces
            ply_data_face_type = ply_data["face"].dtype
            logger.info("Found " + str(len(ply_data["face"].data)) + " faces")
            for line in ply_data["face"].data["vertex_indices"]:
                current_face = Face()
                current_face.vertex_indices = np.array(
                    [line[0], line[1], line[2]]
                )
                faces.append(current_face)

            ply_data_face_data_type = [("vertex_indices", "i4", (3,))]
            face_names = ply_data["face"].data.dtype.names
            if (
                "red" in face_names
                and "green" in face_names
                and "blue" in face_names
            ):
                ply_data_face_data_type = [
                    ("vertex_indices", "i4", (3,)),
                    ("red", "u1"),
                    ("green", "u1"),
                    ("blue", "u1"),
                ]

        return faces, ply_data_face_type, ply_data_face_data_type

    @staticmethod
    def __vertices_to_ply_vertex_element(
        point_list, ply_data_vertex_data_dtype_list
    ):

        ply_data_vertex_data_dtype = np.dtype(ply_data_vertex_data_dtype_list)

        # if measurements are used, then we do not know one dimension of the array
        vertex_output_array = np.empty(
            (len(point_list),), dtype=ply_data_vertex_data_dtype
        )

        with_color = False
        if (
            "red" in ply_data_vertex_data_dtype.names
            and "green" in ply_data_vertex_data_dtype.names
            and "blue" in ply_data_vertex_data_dtype.names
        ):
            with_color = True

        with_normals = False
        if (
            "nx" in ply_data_vertex_data_dtype.names
            and "ny" in ply_data_vertex_data_dtype.names
            and "nz" in ply_data_vertex_data_dtype.names
        ):
            with_normals = True

        with_measurements = "measurements" in ply_data_vertex_data_dtype.names

        # set all the values, offered / defined by property_type_list
        for index, point in enumerate(point_list):

            # row = np.empty(1, dtype=ply_data_vertex_data_dtype)
            vertex_output_array[index]["x"] = point.coord[0]
            vertex_output_array[index]["y"] = point.coord[1]
            vertex_output_array[index]["z"] = point.coord[2]

            if with_color:
                vertex_output_array[index]["red"] = point.color[0]
                vertex_output_array[index]["green"] = point.color[1]
                vertex_output_array[index]["blue"] = point.color[2]

            if with_normals:
                vertex_output_array[index]["nx"] = point.normal[0]
                vertex_output_array[index]["ny"] = point.normal[1]
                vertex_output_array[index]["nz"] = point.normal[2]

            for scalar_key in point.scalars:
                vertex_output_array[index][scalar_key] = point.scalars[
                    scalar_key
                ]

            if with_measurements:
                measurements = []
                for measurement in point.measurements:
                    measurements += measurement.to_list()
                vertex_output_array[index]["measurements"] = measurements

        description = PlyElement.describe(
            vertex_output_array,
            name="vertex",
            # possible values for val_types
            # ['int8', 'i1', 'char', 'uint8', 'u1', 'uchar', 'b1',
            # 'int16', 'i2', 'short', 'uint16', 'u2', 'ushort',
            # 'int32', 'i4', 'int', 'uint32', 'u4', 'uint',
            # 'float32', 'f4', 'float', 'float64', 'f8', 'double']
            val_types={"measurements": "float"},
        )

        return description

    @staticmethod
    def __faces_to_ply_face_element(face_list, property_type_list):

        face_output_array = np.empty(len(face_list), dtype=property_type_list)
        for index, face in enumerate(face_list):

            row = np.empty(1, dtype=property_type_list)
            # We don't use face colors, the color of the faces is defined using
            # the vertex colors!
            row[
                "vertex_indices"
            ] = face.vertex_indices  # face.vertex_indices is a np.array
            face_output_array[index] = row

        output_ply_data_face_element = PlyElement.describe(
            face_output_array, "face"
        )

        return output_ply_data_face_element

    @staticmethod
    def __cameras_2_ply_vertex_element(camera_list, property_type_list):

        camera_output_array = np.empty(
            len(camera_list), dtype=property_type_list
        )

        for index, camera in enumerate(camera_list):

            row = np.empty(1, dtype=property_type_list)
            row["x"] = camera.get_camera_center()[0]
            row["y"] = camera.get_camera_center()[1]
            row["z"] = camera.get_camera_center()[2]

            row["red"] = camera.color[0]
            row["green"] = camera.color[1]
            row["blue"] = camera.color[2]

            row["nx"] = camera.normal[0]
            row["ny"] = camera.normal[1]
            row["nz"] = camera.normal[2]

            camera_output_array[index] = row

        return PlyElement.describe(camera_output_array, "vertex")

    @staticmethod
    def parse_ply_file_extended(ifp):

        logger.info("Parse PLY File: ...")

        ply_data = PlyData.read(ifp)

        (
            vertices,
            ply_data_vertex_dtype,
            ply_data_vertex_data_dtype,
        ) = PLYFileHandler.__ply_data_vertices_to_vetex_list(ply_data)
        (
            faces,
            ply_data_face_type,
            ply_data_face_data_type,
        ) = PLYFileHandler.__ply_data_faces_to_face_list(ply_data)

        logger.info("Parse PLY File: Done")

        # return always 6 arguments. However, the latter may be empty
        return (
            vertices,
            ply_data_vertex_dtype,
            ply_data_vertex_data_dtype,
            faces,
            ply_data_face_type,
            ply_data_face_data_type,
        )

    @staticmethod
    def parse_ply_file(ifp):
        logger.info("Parse PLY File: ...")
        logger.vinfo("ifp", ifp)
        ply_data = PlyData.read(ifp)

        vertices, _, _ = PLYFileHandler.__ply_data_vertices_to_vetex_list(
            ply_data
        )
        faces, _, _ = PLYFileHandler.__ply_data_faces_to_face_list(ply_data)

        logger.info("Parse PLY File: Done")

        return vertices, faces

    @staticmethod
    def write_ply_file_from_vertex_mat(ofp, vertex_mat):
        vertices = []
        for entry in vertex_mat:
            vertices.append(Point(coord=entry))
        PLYFileHandler.write_ply_file(ofp, vertices)

    @staticmethod
    def build_type_list(
        vertices, with_colors, with_normals, with_measurements
    ):
        ply_data_vertex_data_dtype_list = [
            ("x", "<f4"),
            ("y", "<f4"),
            ("z", "<f4"),
        ]
        if with_colors:
            ply_data_vertex_data_dtype_list += [
                ("red", "u1"),
                ("green", "u1"),
                ("blue", "u1"),
            ]
        if with_normals:
            ply_data_vertex_data_dtype_list += [
                ("nx", "<f4"),
                ("ny", "<f4"),
                ("nz", "<f4"),
            ]

        if len(vertices) > 0:
            for scalar_keys in vertices[0].scalars:
                ply_data_vertex_data_dtype_list += [(scalar_keys, "<f4")]

            if with_measurements:
                # since the length of the measurements varies, we use an object data type here
                ply_data_vertex_data_dtype_list += [("measurements", object)]
        return ply_data_vertex_data_dtype_list

    @staticmethod
    def write_ply_file(
        ofp,
        vertices,
        with_colors=True,
        with_normals=False,
        faces=None,
        plain_text_output=False,
        with_measurements=False,
    ):

        logger.info("write_ply_file: " + ofp)

        ply_data_vertex_data_dtype_list = PLYFileHandler.build_type_list(
            vertices, with_colors, with_normals, with_measurements
        )

        logger.vinfo(
            "ply_data_vertex_data_dtype_list", ply_data_vertex_data_dtype_list
        )

        output_ply_data_vertex_element = (
            PLYFileHandler.__vertices_to_ply_vertex_element(
                vertices, ply_data_vertex_data_dtype_list
            )
        )

        if faces is None or len(faces) == 0:
            logger.info("Write File With Vertices Only (no faces)")
            output_data = PlyData(
                [output_ply_data_vertex_element], text=plain_text_output
            )
        else:
            logger.info("Write File With Faces")
            logger.info("Number faces" + str(len(faces)))

            ply_data_face_data_type = [("vertex_indices", "i4", (3,))]

            # we do not define colors for faces,
            # since we use the vertex colors to colorize the face

            output_ply_data_face_element = (
                PLYFileHandler.__faces_to_ply_face_element(
                    faces, ply_data_face_data_type
                )
            )
            output_data = PlyData(
                [output_ply_data_vertex_element, output_ply_data_face_element],
                text=plain_text_output,
            )

        output_data.write(ofp)

    @staticmethod
    def write_camera_ply_file(ofp, cameras, plain_text_output=True):

        ply_data_vertex_data_dtype_list = [
            ("x", "<f4"),
            ("y", "<f4"),
            ("z", "<f4"),
        ]
        ply_data_vertex_data_dtype_list += [
            ("red", "u1"),
            ("green", "u1"),
            ("blue", "u1"),
        ]
        ply_data_vertex_data_dtype_list += [
            ("nx", "<f4"),
            ("ny", "<f4"),
            ("nz", "<f4"),
        ]

        ply_data_vertex_data_dtype = np.dtype(ply_data_vertex_data_dtype_list)

        output_ply_data_vertex_element = (
            PLYFileHandler.__cameras_2_ply_vertex_element(
                cameras, ply_data_vertex_data_dtype
            )
        )

        # [('x', '<f4'), ('y', '<f4'), ('z', '<f4'), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')]

        logger.info("Write (Camera) File With Vertices Only (no faces)")
        output_data = PlyData(
            [output_ply_data_vertex_element], text=plain_text_output
        )

        output_data.write(ofp)

    @staticmethod
    def read_and_write_test(ifp, ofp):
        vertices, faces = PLYFileHandler.parse_ply_file(ifp)
        PLYFileHandler.write_ply_file(ofp, vertices, faces=faces)


if __name__ == "__main__":

    ply_ofp = "out.ply"

    measurements1 = [
        Measurement(1222.428, 2, 3, 4),
        Measurement(8, 9, 10.1, 11.2),
        Measurement(28, 29, 30, 31),
        Measurement(12213, 29, 30, 31),
    ]
    measurements2 = [Measurement(11, 12, 13, 14), Measurement(18, 19, 20, 21)]
    p_1 = Point([0, 0, 0])
    p_1.measurements = measurements1
    p_2 = Point([0, 0, 1])
    p_2.measurements = measurements1
    p_3 = Point([0, 1, 1])
    p_3.measurements = measurements2
    p_4 = Point([1, 0, 0])
    p_4.measurements = measurements2
    p_5 = Point([1, 1, 1])
    p_5.measurements = measurements2
    points = [p_1, p_2, p_3, p_4, p_5]

    PLYFileHandler.write_ply_file(
        ply_ofp, points, plain_text_output=True, with_measurements=True
    )

    vertices, faces = PLYFileHandler.parse_ply_file(ply_ofp)
    p_1, p_2, p_3, p_4, p_5 = vertices
    for p in vertices:
        logger.info(p.coord, p.color, p.measurements)
