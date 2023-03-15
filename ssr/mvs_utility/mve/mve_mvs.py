import os

from ssr.utility.logging_extension import logger
from ssr.mvs_utility.mve.mve_texrecon import MVETexrecon
from ssr.mvs_utility.mve.mve_creator import MVECreator
from ssr.mvs_utility.mve.multiscale_fusion import MultiScaleReconstructor


class MVEMVSReconstructor:

    # https://www.gcc.tu-darmstadt.de/home/proj/mve/
    # https://www.gcc.tu-darmstadt.de/home/proj/texrecon/
    # https://github.com/simonfuhrmann/mve/wiki/MVE-Users-Guide

    @staticmethod
    def get_point_cloud_with_scale_ply_ofp(mve_workspace):
        return os.path.join(mve_workspace, "mve_point_cloud.ply")

    def create_scene_from_sfm_result(
        self, ifp_or_idp, mve_workspace, downscale_level=-1, lazy=False
    ):
        views_folder = os.path.join(mve_workspace, "views")
        if os.path.isdir(mve_workspace) and os.path.isdir(views_folder) and lazy:
            return
        mve_creator = MVECreator(workspace_dp=mve_workspace)
        mve_creator.create_scene_from_sfm_result(ifp_or_idp, downscale_level)

    def import_images_to_scene(self, image_idp, mve_workspace):
        mve_creator = MVECreator(workspace_dp=mve_workspace)
        mve_creator.import_images_to_scene(image_idp)

    def compute_depth_maps(self, mve_workspace, downscale_level=0):
        mve_creator = MVECreator(workspace_dp=mve_workspace)
        mve_creator.compute_depth_maps(downscale_level=downscale_level)

    def compute_dense_point_cloud_from_depth_maps(
        self,
        mve_workspace,
        point_cloud_with_scale_ply_ofp=None,
        downscale_level=0,
        view_ids=None,
        fssr_output=True,
        lazy=False,
    ):
        mve_creator = MVECreator(workspace_dp=mve_workspace)
        if point_cloud_with_scale_ply_ofp is None:
            point_cloud_with_scale_ply_ofp = (
                mve_creator.get_point_cloud_with_scale_ply_fp()
            )

        if not os.path.isfile(point_cloud_with_scale_ply_ofp) or not lazy:
            mve_creator.compute_dense_point_cloud_from_depth_maps(
                point_cloud_with_scale_ply_ofp,
                downscale_level=downscale_level,
                view_ids=view_ids,
                fssr_output=fssr_output,
            )

    def compute_fssr_reconstruction(
        self,
        mve_workspace,
        point_cloud_with_scale_ply_ifp=None,
        mesh_ply_ofp=None,
        lazy=False,
    ):
        mve_creator = MVECreator(workspace_dp=mve_workspace)
        if point_cloud_with_scale_ply_ifp is None:
            point_cloud_with_scale_ply_ifp = (
                mve_creator.get_point_cloud_with_scale_ply_fp()
            )
        if mesh_ply_ofp is None:
            mesh_ply_ofp = mve_creator.get_mesh_ply_fp()

        if not os.path.isfile(mesh_ply_ofp) or not lazy:
            mve_creator.compute_fssr_mesh_from_point_cloud(
                point_cloud_with_scale_ply_ifp, mesh_ply_ofp
            )

    def compute_gdmr_reconstruction(
        self,
        mve_workspace,
        point_cloud_with_scale_ply_ifp=None,
        mesh_ply_ofp=None,
        lazy=False,
    ):
        mve_creator = MVECreator(workspace_dp=mve_workspace)
        if point_cloud_with_scale_ply_ifp is None:
            point_cloud_with_scale_ply_ifp = (
                mve_creator.get_point_cloud_with_scale_ply_fp()
            )
        if mesh_ply_ofp is None:
            mesh_ply_ofp = mve_creator.get_mesh_ply_fp()

        if not os.path.isfile(mesh_ply_ofp) or not lazy:
            msr = MultiScaleReconstructor()
            msr.create_mesh_from_point_cloud(
                point_cloud_with_scale_ply_ifp, mve_workspace, mesh_ply_ofp
            )

    def compute_clean_mesh(
        self,
        mve_workspace,
        mesh_ply_ifp=None,
        mesh_cleaned_ply_ofp=None,
        delete_color=True,
        lazy=False,
    ):
        mve_creator = MVECreator(workspace_dp=mve_workspace)
        if mesh_ply_ifp is None:
            mesh_ply_ifp = mve_creator.get_mesh_ply_fp()
        if mesh_cleaned_ply_ofp is None:
            mesh_cleaned_ply_ofp = mve_creator.get_mesh_cleaned_ply_fp()

        if not os.path.isfile(mesh_cleaned_ply_ofp) or not lazy:
            mve_creator.compute_cleaned_mesh(
                mesh_ply_ifp,
                mesh_cleaned_ply_ofp,
                delete_color=delete_color,
                delete_scale=True,
                delete_conf=True,
            )

    def compute_texture(
        self,
        mve_workspace,
        mesh_cleaned_ply_ifp=None,
        mesh_textured_odp=None,
    ):

        if mesh_cleaned_ply_ifp is None:
            mesh_cleaned_ply_ifp = os.path.join(mve_workspace, "mve_mesh_cleaned.ply")
        if mesh_textured_odp is None:
            mesh_textured_odp = os.path.join(mve_workspace, "mve_mesh_textured")

        texrecon = MVETexrecon()
        texrecon.create_textured_mesh(
            mve_scene_idp=mve_workspace,
            untextured_mesh_ifp=mesh_cleaned_ply_ifp,
            texture_odp=mesh_textured_odp,
        )

    def create_textured_mesh_from_nvm_and_mesh(
        self,
        nvm_ifp,
        untextured_mesh_ifp,
        mve_workspace,
        texture_odp,
        lazy=True,
    ):

        logger.info("create_textured_mesh_from_nvm: ...")
        mve_creator = MVECreator(workspace_dp=mve_workspace)
        if not lazy or not os.path.isdir(mve_workspace):
            mve_creator.create_scene_from_sfm_result(nvm_ifp)

        texrecon = MVETexrecon()
        texrecon.create_textured_mesh(mve_workspace, untextured_mesh_ifp, texture_odp)
        logger.info("create_textured_mesh_from_nvm: Done")
