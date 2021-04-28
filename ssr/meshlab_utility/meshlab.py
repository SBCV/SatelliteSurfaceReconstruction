import tempfile
import subprocess
import os
from ssr.utility.logging_extension import logger
import xml.etree.ElementTree as ET
from ssr.config.ssr_config import SSRConfig


class _MLXFileHandler:
    @staticmethod
    def get_value_as_str(mlx_ifp, target_name):
        tree = ET.parse(mlx_ifp)
        meshlab_filter_script = tree.getroot()
        meshlab_filter = meshlab_filter_script.find("filter")
        result = None
        for parameter in meshlab_filter:
            if parameter.tag != "Param":
                continue
            if parameter.attrib["name"] == target_name:
                result = parameter.attrib["value"]
        if result is None:
            assertion_msg = (
                f"Did not find parameter tag {parameter.tag}"
                + f" with attribute {target_name}"
            )
            assert False, assertion_msg
        return result

    @staticmethod
    def set_value(mlx_ofp, target_name, value):
        tree = ET.parse(mlx_ofp)
        meshlab_filter_script = tree.getroot()
        meshlab_filter = meshlab_filter_script.find("filter")
        for parameter in meshlab_filter:
            if parameter.tag != "Param":
                continue
            if parameter.attrib["name"] == target_name:
                parameter.attrib["value"] = str(value)
        tree.write(open(mlx_ofp, "w"), encoding="unicode")


class Meshlab:
    """This is an interface to the meshlab command line mode."""

    def __init__(self):
        ssr_config = SSRConfig.get_instance()
        self.executable_fp = ssr_config.get_option_value(
            "meshlab_server_fp", str
        )
        self.meshlab_temp_dp = ssr_config.get_option_value(
            "meshlab_temp_dp", str
        )

    def _create_lmx_template(self, template_fn):
        assert template_fn in [
            "montecarlo_sampling.mlx",
            "simplification_quadric_edge_collapse_decimation.mlx",
            "stratified_triangle_sampling.mlx",
            "poisson_disk_sampling.mlx",
        ], f"Received unsupported template_fn: {template_fn}"
        mlx_template_ifp = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            os.path.join("mlx", template_fn),
        )
        tmp_file = tempfile.NamedTemporaryFile(
            suffix=".mlx", dir=self.meshlab_temp_dp, delete=False
        )
        tmp_ofp = tmp_file.name
        tree = ET.parse(mlx_template_ifp)
        tree.write(open(tmp_ofp, "w"), encoding="unicode")

        return tmp_ofp

    def create_mesh(self, point_cloud_ifp, mesh_ofp):

        template_fp_1 = self._create_lmx_template(
            "compute_normals_for_point_sets.mlx"
        )
        template_fp_2 = self._create_lmx_template(
            "surface_reconstruction_screened_poisson.mlx"
        )

        options = []
        options += ["-i", point_cloud_ifp]
        options += ["-o", mesh_ofp]
        options += ["-s", template_fp_1]
        subprocess.call([Meshlab.executable_fp] + options)

        options = []
        options += ["-i", mesh_ofp]
        options += ["-o", mesh_ofp]
        options += ["-s", template_fp_2]
        subprocess.call([Meshlab.executable_fp] + options)

        # Remove the file from the file system
        os.unlink(template_fp_1)
        os.unlink(template_fp_2)

    def decimate_mesh(self, mesh_ifp, mesh_ofp):
        # In meshlab_utility:
        #   Filters /
        #       Remeshing, Simplfification and Reconstruction /
        #           Simplification: Quadric Edge Collapse Decimation

        template_fp = self._create_lmx_template(
            "simplification_quadric_edge_collapse_decimation.mlx"
        )

        options = []
        options += ["-i", mesh_ifp]
        options += ["-o", mesh_ofp]
        options += ["-m", "vc"]
        options += ["-s", template_fp]
        # Although, this does potentially print a message like
        # "no additional memory available!!! memory required: 490700136"
        # it works as expected
        subprocess.call([self.executable_fp] + options)

        # Remove the file from the file system
        os.unlink(template_fp)

    def compute_hausdorff_distance(self, mesh_1_ifp, mesh_2_ifp, result_ofp):

        # In meshlab_utility:
        #   Filters / Sampling / Hausdorff Distance
        template_fp = self._create_lmx_template("hausdorff_distance.mlx")

        options = []
        options += ["-l", result_ofp]
        options += ["-i", mesh_1_ifp]
        options += ["-i", mesh_2_ifp]
        options += ["-s", template_fp]

        subprocess.call([self.executable_fp] + options)
        # Remove the file from the file system
        os.unlink(template_fp)

    def sample_mesh(
        self, mesh_ifp, point_cloud_ofp, num_vertices, sampling_method
    ):
        # While meshlab provides a variety of sampling methods,
        # Cloudcompare provides only a single method that randomly samples
        # points.

        assert sampling_method in [
            "poisson_disk",
            "stratified_triangle",
            "montecarlo",
        ], f"Received unsupported sampling method: {sampling_method}"

        #   Poisson-disk Sampling
        #       Requires the definition of
        #           number of samples OR radius or percentage
        #   Stratified Triangle Sampling
        #       Requires the definition of number of samples
        #       Results look better than Monte Carlo Sampling

        template_fp = self._create_lmx_template(
            sampling_method + "_sampling.mlx"
        )
        logger.vinfo("template_fp", template_fp)
        assert os.path.isfile(template_fp)

        _MLXFileHandler.set_value(template_fp, "SampleNum", num_vertices)
        num_vertices_str = _MLXFileHandler.get_value_as_str(
            template_fp, "SampleNum"
        )
        assertion_msg = f"{num_vertices_str} vs {num_vertices}"
        assert int(num_vertices_str) == num_vertices, assertion_msg

        options = []
        options += ["-i", mesh_ifp]
        options += ["-s", template_fp]
        options += ["-o", point_cloud_ofp]

        call_list = [self.executable_fp] + options
        logger.vinfo("call_list", call_list)
        subprocess.call(call_list)

        # Remove the file from the file system
        os.unlink(template_fp)

    def remove_color(self, mesh_ifp, mesh_ofp):
        options = []
        options += ["-i", mesh_ifp]
        options += ["-o", mesh_ofp]
        subprocess.call([self.executable_fp] + options)


if __name__ == "__main__":

    meshlab = Meshlab()

    mesh_ifp = "/path/to/mesh.ply"
    point_cloud_ofp = "/path/to/point_cloud.ply"
    num_vertices = 1000
    meshlab.sample_mesh(mesh_ifp, point_cloud_ofp, num_vertices, "montecarlo")

    mesh_ifp = "/path/to/mesh_with_vertex_color.ply"
    point_cloud_ofp = "/path/to/mesh_without_vertex_color.ply"
    meshlab.remove_color(mesh_ifp, point_cloud_ofp)
