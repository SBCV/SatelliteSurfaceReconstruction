import os
from ssr.utility.logging_extension import logger
from ssr.mvs_utility.mve.mve_mvs import MVEMVSReconstructor


class TexturingStep:
    @staticmethod
    def compute_texturing_with_openmvs(colmap_idp, odp):
        openmvs_mesh_textured_mvs_fn = "openmvs_mesh_textured.mvs"

        # pm = self.pm
        # # This step already imports the dense point cloud computed by colmap
        # # (Stored in fused.ply and fused.ply.vis)
        # OpenMVSReconstructor.convert_colmap_to_openMVS(
        #     colmap_dense_idp=pm.colmap_workspace_dp,
        #     openmvs_workspace_dp=pm.openmvs_workspace_dp,
        #     openmvs_ofn=openmvs_interface_mvs_fn,
        #     image_folder="images/",
        # )
        #
        # export_type = "ply"
        # refined_fp = os.path.join(
        #     pm.openmvs_workspace_dp, openmvs_mesh_refined_mvs_fn
        # )
        # if os.path.isfile(refined_fp):
        #     mesh_ifp = openmvs_mesh_refined_mvs_fn
        # else:
        #     mesh_ifp = openmvs_mesh_mvs_fn
        #
        # OpenMVSReconstructor.texture_mesh(
        #     pm.openmvs_workspace_dp,
        #     mesh_ifp,
        #     openmvs_mesh_textured_mvs_fn,
        #     export_type,
        # )

    @staticmethod
    def compute_texturing_with_mve(
        colmap_idp, mesh_ifp, texturing_odp, lazy=True
    ):
        logger.info("compute_texturing_with_mve: ...")
        logger.info(f"colmap_idp: {colmap_idp}")
        logger.info(f"mesh_ifp: {mesh_ifp}")
        logger.info(f"texturing_odp: {texturing_odp}")

        mve_odp = os.path.dirname(texturing_odp)
        mve_mvs_reconstructor = MVEMVSReconstructor()

        # Import the colmap reconstruction into MVE exactly once,
        # since it is identical for all reconstructions.
        if not os.path.isdir(mve_odp):
            mve_mvs_reconstructor.create_scene_from_sfm_result(
                colmap_idp, mve_odp, downscale_level=-1, lazy=lazy
            )

        mve_mvs_reconstructor.compute_texture(
            mve_workspace=mve_odp,
            mesh_cleaned_ply_ifp=mesh_ifp,
            mesh_textured_odp=texturing_odp,
        )

        logger.info("compute_texturing_with_mve: Done")
