import os
import subprocess
from ssr.utility.logging_extension import logger
from ssr.config.ssr_config import SSRConfig


class ColmapMVSReconstructor:
    def __init__(self):
        self.ssr_config = SSRConfig.get_instance()
        self.colmap_exe_dp = self.ssr_config.colmap_exe_dp

    def reconstruct_mesh_with_poisson(
        self, point_cloud_ply_ifp, mesh_ply_ofp, poisson_trim_thresh, lazy
    ):
        logger.info("reconstruct_mesh: ...")
        logger.vinfo("mesh_ply_ofp", mesh_ply_ofp)

        assert os.path.isdir(self.colmap_exe_dp)
        assert os.path.isfile(os.path.join(self.colmap_exe_dp, "colmap"))
        if not os.path.isfile(mesh_ply_ofp) or not lazy:
            os.environ["PATH"] += os.pathsep + self.colmap_exe_dp
            trim_thresh_str = str(poisson_trim_thresh)
            dense_mesher_call = [
                "colmap",
                "poisson_mesher",
                "--input_path",
                point_cloud_ply_ifp,
                "--output_path",
                mesh_ply_ofp,
                "--PoissonMeshing.trim",
                trim_thresh_str,
            ]
            logger.vinfo("dense_mesher_call: ", dense_mesher_call)
            subprocess.call(dense_mesher_call)

        logger.info("reconstruct_mesh: Done")

    def reconstruct_mesh_with_delaunay(
        self,
        reconstruction_idp,
        mesh_ply_ofp,
        max_proj_dist=None,
        max_depth_dist=None,
        lazy=False,
    ):

        logger.info("reconstruct_mesh: ...")

        assert os.path.isdir(self.colmap_exe_dp)
        assert os.path.isfile(os.path.join(self.colmap_exe_dp, "colmap"))
        if not os.path.isfile(mesh_ply_ofp) or not lazy:
            os.environ["PATH"] += os.pathsep + self.colmap_exe_dp

            dense_mesher_call = [
                "colmap",
                "delaunay_mesher",
                "--input_path",
                reconstruction_idp,
                "--output_path",
                mesh_ply_ofp,
                "--input_type",
                "dense",
            ]

            if max_proj_dist is not None:
                dense_mesher_call += [
                    "--DelaunayMeshing.max_proj_dist",
                    str(max_proj_dist),
                ]

            if max_depth_dist is not None:
                dense_mesher_call += [
                    "--DelaunayMeshing.max_depth_dist",
                    str(max_depth_dist),
                ]

            logger.vinfo("dense_mesher_call: ", dense_mesher_call)
            subprocess.call(dense_mesher_call)

        logger.info("reconstruct_mesh: Done")
