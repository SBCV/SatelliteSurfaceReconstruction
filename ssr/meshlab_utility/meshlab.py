import tempfile
import os
from ssr.utility.logging_extension import logger
import xml.etree.ElementTree as ET
from ssr.config.ssr_config import SSRConfig
from ssr.utility.os_extension import makedirs_safely
import pymeshlab


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
    """This is an interface to the meshlab command line mode.

    https://github.com/cnr-isti-vclab/PyMeshLab
    https://pymeshlab.readthedocs.io/en/latest/tutorials/apply_filter.html
    https://pymeshlab.readthedocs.io/en/latest/tutorials/filter_script_load_and_apply.html
    https://pymeshlab.readthedocs.io/en/latest/tutorials/filter_script_create_and_save.html#filter-script-create-and-save

    https://pymeshlab.readthedocs.io/en/latest/filter_list.html
    """

    def __init__(self, executable_fp, meshlab_temp_dp):
        self.executable_fp = executable_fp
        self.meshlab_temp_dp = meshlab_temp_dp
        if self.meshlab_temp_dp is not None:
            if not os.path.isdir(self.meshlab_temp_dp):
                logger.vinfo("meshlab_temp_dp", self.meshlab_temp_dp)
                assert (
                    False
                ), "Choose a valid path (in the config file) for Meshlab's temp directory"

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
        makedirs_safely(self.meshlab_temp_dp)
        tmp_file = tempfile.NamedTemporaryFile(
            suffix=".mlx", dir=self.meshlab_temp_dp, delete=False
        )
        tmp_ofp = tmp_file.name
        tree = ET.parse(mlx_template_ifp)
        tree.write(open(tmp_ofp, "w"), encoding="unicode")

        return tmp_ofp

    def sample_mesh(
        self, mesh_ifp, point_cloud_ofp, num_vertices, sampling_method
    ):
        # While meshlab provides a variety of sampling methods,
        # Cloudcompare provides only a single method that randomly samples
        # points.
        # https://pymeshlab.readthedocs.io/en/latest/filter_scripts.html

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

        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(mesh_ifp)
        ms.load_filter_script(template_fp)
        ms.apply_filter_script()
        ms.save_current_mesh(point_cloud_ofp)

    def remove_color(self, mesh_ifp, mesh_ofp):
        # https://pymeshlab.readthedocs.io/en/latest/io_format_list.html#save-mesh-parameters
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(mesh_ifp)
        ms.save_current_mesh(
            mesh_ofp,
            save_vertex_color=False,
        )


if __name__ == "__main__":
    ssr_config = SSRConfig.get_instance()
    meshlab = Meshlab(
        executable_fp=ssr_config.meshlab_server_fp,
        meshlab_temp_dp=ssr_config.meshlab_temp_dp,
    )

    mesh_ifp = "/path/to/mesh.ply"
    point_cloud_ofp = "/path/to/point_cloud.ply"
    num_vertices = 1000
    meshlab.sample_mesh(mesh_ifp, point_cloud_ofp, num_vertices, "montecarlo")

    mesh_ifp = "/path/to/mesh_with_vertex_color.ply"
    point_cloud_ofp = "/path/to/mesh_without_vertex_color.ply"
    meshlab.remove_color(mesh_ifp, point_cloud_ofp)
