import os
from ssr.utility.logging_extension import logger


class PathManager:
    def __init__(
        self,
        pan_ntf_idp,
        msi_ntf_idp,
        rgb_tif_idp,
        vissat_workspace_dp,
        ssr_workspace_dp,
    ):

        self.vissat_workspace_dp = vissat_workspace_dp
        self.pan_ntf_idp = pan_ntf_idp
        self.msi_ntf_idp = msi_ntf_idp
        self.rgb_tif_idp = rgb_tif_idp
        self.ssr_workspace_dp = ssr_workspace_dp

        # === Input Colmap VisSat File Paths ===
        self.vissat_config_fp = os.path.join(
            self.vissat_workspace_dp,
            "VisSat.json",
        )

        self.rec_pan_png_idp = os.path.join(self.vissat_workspace_dp, "images")
        # The name of the meta data in the vissat_workspace_dp (i.e. "metas")
        # is hardcoded in the VisSatSatelliteStereo library
        self.vissat_meta_data_idp = os.path.join(self.vissat_workspace_dp, "metas")

        self.vissat_mvs_workspace_dp = os.path.join(
            self.vissat_workspace_dp, "colmap", "mvs"
        )
        self.sparse_model_with_skew_idp = os.path.join(
            self.vissat_mvs_workspace_dp, "sparse"
        )
        self.depth_map_reparam_with_skew_idp = os.path.join(
            self.vissat_mvs_workspace_dp, "stereo", "depth_maps"
        )
        self.last_rows_ifp = os.path.join(self.vissat_mvs_workspace_dp, "last_rows.txt")
        self.fused_ifp = os.path.join(self.vissat_mvs_workspace_dp, "fused.ply")
        self.fused_vis_ifp = os.path.join(self.vissat_mvs_workspace_dp, "fused.ply.vis")

        # === Output Workspace File Paths ===

        # Pan Images (with skew)
        self.pan_workspace_dp = os.path.join(self.ssr_workspace_dp, "pan")
        self.pan_png_idp = os.path.join(self.pan_workspace_dp, "images")

        self.pan_config_fp = os.path.join(self.pan_workspace_dp, "extract_pan.json")

        # MSI Images (with skew)
        self.msi_workspace_dp = os.path.join(self.ssr_workspace_dp, "msi")
        self.msi_png_idp = os.path.join(self.msi_workspace_dp, "images")
        self.msi_config_fp = os.path.join(self.msi_workspace_dp, "extract_msi.json")

        # Sharpened Images (with skew)
        self.sharpened_with_skew_png_dp = os.path.join(
            self.ssr_workspace_dp, "sharpened_with_skew"
        )

        # Colmap Workspace (Camera models, images and depth maps WITHOUT skew)
        # Contains (in addition) also depth maps WITH skew.
        self.colmap_workspace_no_skew_dp = os.path.join(self.ssr_workspace_dp, "colmap")

        # Colmap reconstruction, Images and Depth Maps without skew
        self.sparse_model_no_skew_dp = os.path.join(
            self.colmap_workspace_no_skew_dp, "sparse"
        )
        self.sharpened_no_skew_png_dp = os.path.join(
            self.colmap_workspace_no_skew_dp, "images"
        )
        # Depth Maps (no skew)
        self.depth_map_real_no_skew_dp = os.path.join(
            self.colmap_workspace_no_skew_dp, "stereo", "depth_maps"
        )
        # Depth Maps (with skew)
        self.depth_map_real_with_skew_dp = os.path.join(
            self.colmap_workspace_no_skew_dp,
            "stereo",
            "depth_map_real_with_skew",
        )

        # Additional results (no skew)
        self.pan_no_skew_png_dp = os.path.join(self.ssr_workspace_dp, "pan_no_skew")

        # Fused results (skew agnostic)
        #   The fused files do NOT contain information about the location of
        #   the observations.
        #   The files only store, which point is visible in which image.
        self.fused_ofp = os.path.join(self.colmap_workspace_no_skew_dp, "fused.ply")
        self.fused_vis_no_skew_ofp = os.path.join(
            self.colmap_workspace_no_skew_dp, "fused.ply.vis"
        )

        # Surface workspace
        self.surface_workspace_dp = os.path.join(self.ssr_workspace_dp, "surface")

        # Meshing workspace
        self.mesh_workspace_dp = os.path.join(self.surface_workspace_dp, "meshing")
        self.mesh_colmap_workspace_dp = os.path.join(self.mesh_workspace_dp, "colmap")
        self.mesh_openmvs_workspace_dp = os.path.join(self.mesh_workspace_dp, "openmvs")
        self.mesh_mve_workspace_dp = os.path.join(self.mesh_workspace_dp, "mve")

        self.mesh_ply_ofn = "mesh.ply"
        self.plain_mesh_ply_ofn = "plain_mesh.ply"
        self.plain_mesh_refined_ply_ofn = "plain_mesh_refined.ply"

        # Texturing workspace
        self.texturing_workspace_dp = os.path.join(self.surface_workspace_dp, "surface")
        self.texturing_openmvs_workspace_dp = os.path.join(
            self.texturing_workspace_dp, "openMVS"
        )
        self.texturing_mve_workspace_dp = os.path.join(
            self.texturing_workspace_dp, "mve"
        )
        self.texturing_open3d_workspace_dp = os.path.join(
            self.texturing_workspace_dp, "open3d"
        )

    def check_vissat_workspace(self):
        if not os.path.isdir(self.vissat_workspace_dp):
            logger.vinfo("self.vissat_workspace_dp", self.vissat_workspace_dp)
            assert False, "Vissat output directory missing"

    def check_rec_pan_png_idp(self):
        if not os.path.isdir(self.rec_pan_png_idp):
            logger.vinfo("self.rec_pan_png_idp", self.rec_pan_png_idp)
            assert False
