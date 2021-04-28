import os
from ssr.meshlab_utility.meshlab import Meshlab

from ssr.mvs_utility.colmap.colmap_mvs import (
    ColmapMVSReconstructor,
)
from ssr.mvs_utility.openmvs.openmvs_mvs import (
    OpenMVSReconstructor,
)
from ssr.mvs_utility.mve.mve_mvs import (
    MVEMVSReconstructor,
)
from ssr.utility.logging_extension import logger


class MeshingStep:
    @staticmethod
    def compute_mesh_with_colmap(
        colmap_idp,
        mesh_odp,
        mesh_ply_ofn,
        plain_mesh_ply_ofn,
        meshing_algo,
        poisson_trim_thresh=10,
        lazy=False,
    ):
        """Poisson meshing works with a single point-cloud-ply-file, whereas
        delaunay meshing requires a full workspace.
        """
        logger.info("compute_mesh_with_colmap: ...")
        assert meshing_algo in ["poisson_mesher", "delaunay_mesher"]
        mesh_ply_ofp = os.path.join(mesh_odp, mesh_ply_ofn)
        logger.vinfo("ofp", mesh_ply_ofp)
        colmap_mvs_reconstructor = ColmapMVSReconstructor()
        if meshing_algo == "poisson_mesher":
            point_cloud_ply_ifp = os.path.join(colmap_idp, "fused.ply")
            colmap_mvs_reconstructor.reconstruct_mesh_with_poisson(
                point_cloud_ply_ifp,
                mesh_ply_ofp,
                poisson_trim_thresh,
                lazy=lazy,
            )
        elif meshing_algo == "delaunay_mesher":
            colmap_mvs_reconstructor.reconstruct_mesh_with_delaunay(
                colmap_idp,
                mesh_ply_ofp,
                # https://colmap.github.io/faq.html
                max_proj_dist=0,  # Colmap Default Value: 2.5
                lazy=lazy,
            )
        plain_mesh_ply_ofp = os.path.join(mesh_odp, plain_mesh_ply_ofn)
        meshlab = Meshlab()
        meshlab.remove_color(mesh_ply_ofp, plain_mesh_ply_ofp)

        logger.info("compute_mesh_with_colmap: Done")

    @staticmethod
    def compute_mesh_with_openmvs(
        colmap_idp, odp, mesh_ply_ofn, plain_mesh_ply_ofn, lazy=False
    ):

        logger.info("compute_mesh_with_openmvs: ...")

        # https://github.com/cdcseacave/openMVS/wiki/Usage
        #   Exporting and Viewing Results
        #   Each of the following commands also writes a PLY file that can be
        #   used with many third-party tools. Alternatively, Viewer can be used
        #   to export the MVS projects to PLY or OBJ formats.

        interface_mvs_fn = "interface_colmap.mvs"
        # This will create a "plain_mesh.ply" file
        mesh_mvs_fn = os.path.splitext(mesh_ply_ofn)[0] + ".mvs"

        openmvs_mvs_reconstructor = OpenMVSReconstructor()
        # This step already imports the dense point cloud computed by colmap
        # (Stored in fused.ply and fused.ply.vis)
        openmvs_mvs_reconstructor.convert_colmap_to_openMVS(
            colmap_dense_idp=colmap_idp,
            openmvs_workspace_dp=odp,
            openmvs_ofn=interface_mvs_fn,
            image_folder="images/",
            lazy=lazy,
        )

        logger.vinfo("ofp", os.path.join(odp, mesh_ply_ofn))
        # Adjust the default parameters (min_point_distance=2.5,
        # smoothing_iterations=2) to improve satellite reconstruction results
        min_point_distance = 0
        smoothing_iterations = 0

        openmvs_mvs_reconstructor.reconstruct_mesh(
            odp,
            interface_mvs_fn,
            mesh_mvs_fn,
            # OpenMVS Default Value: min_point_distance=2.5
            min_point_distance=min_point_distance,
            # Clean options:
            # OpenMVS Default Value: decimate_value=1.0
            decimate_value=1.0,
            # OpenMVS Default Value: smoothing_iterations=2
            smoothing_iterations=smoothing_iterations,
            lazy=lazy,
        )
        mesh_ply_ofp = os.path.join(odp, mesh_ply_ofn)
        plain_mesh_ply_ofp = os.path.join(odp, plain_mesh_ply_ofn)
        meshlab = Meshlab()
        meshlab.remove_color(mesh_ply_ofp, plain_mesh_ply_ofp)

        logger.info("compute_mesh_with_openmvs: Done")

    @staticmethod
    def compute_mesh_with_mve(
        colmap_idp,
        odp,
        mesh_ply_ofn,
        plain_mesh_ply_ofn,
        meshing_algo,
        lazy=False,
    ):
        logger.info("compute_mesh_with_mve: ...")
        mesh_ply_ofp = os.path.join(odp, mesh_ply_ofn)
        plain_mesh_ply_ofp = os.path.join(odp, plain_mesh_ply_ofn)
        downscale_level = 0

        mve_mvs_reconstructor = MVEMVSReconstructor()
        mve_mvs_reconstructor.create_scene_from_sfm_result(
            colmap_idp, odp, downscale_level=downscale_level, lazy=lazy
        )
        mve_mvs_reconstructor.compute_dense_point_cloud_from_depth_maps(
            odp,
            downscale_level=downscale_level,
            view_ids=None,
            fssr_output=True,
            lazy=lazy,
        )

        meshlab = Meshlab()
        if meshing_algo == "fssr":
            mve_mvs_reconstructor.compute_fssr_reconstruction(
                odp, mesh_ply_ofp=mesh_ply_ofp, lazy=lazy
            )
            stem, ext = os.path.splitext(mesh_ply_ofp)
            cleaned_mesh_ply_ofp = stem + "_cleaned" + ext
            mve_mvs_reconstructor.compute_clean_mesh(
                odp,
                mesh_ply_ifp=mesh_ply_ofp,
                mesh_cleaned_ply_ofp=cleaned_mesh_ply_ofp,
                delete_color=False,
                lazy=lazy,
            )
            meshlab.remove_color(cleaned_mesh_ply_ofp, plain_mesh_ply_ofp)
        elif meshing_algo == "gdmr":
            mve_mvs_reconstructor.compute_gdmr_reconstruction(
                odp, mesh_ply_ofp=mesh_ply_ofp, lazy=lazy
            )
            meshlab.remove_color(mesh_ply_ofp, plain_mesh_ply_ofp)
        else:
            logger.vinfo("meshing_algo", meshing_algo)
            assert False

        logger.vinfo("ofp", mesh_ply_ofp)
        logger.info("compute_mesh_with_mve: Done")
