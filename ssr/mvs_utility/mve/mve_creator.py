import os
import subprocess
import platform

from ssr.utility.logging_extension import logger
from ssr.config.ssr_config import SSRConfig


class MVECreator:
    def __init__(self, workspace_dp=None):
        self.ssr_config = SSRConfig.get_instance()
        self.mve_apps_dp = self.ssr_config.get_option_value("mve_apps_dp", str)
        self.workspace_folder = workspace_dp

        if platform.system() == "windows":
            self.make_scene_fp = os.path.join(self.mve_apps_dp, "makescene")
            self.sfm_recon_fp = os.path.join(self.mve_apps_dp, "sfmrecon")
            self.dm_recon_fp = os.path.join(self.mve_apps_dp, "dmrecon")
            self.scene2pset_fp = os.path.join(self.mve_apps_dp, "scene2pset")
            self.fssrecon_fp = os.path.join(self.mve_apps_dp, "fssrecon")
            self.meshclean_fp = os.path.join(self.mve_apps_dp, "meshclean")

        else:  # assume linux
            self.make_scene_fp = os.path.join(
                self.mve_apps_dp, "makescene", "makescene"
            )
            self.sfm_recon_fp = os.path.join(
                self.mve_apps_dp, "sfmrecon", "sfmrecon"
            )
            self.dm_recon_fp = os.path.join(
                self.mve_apps_dp, "dmrecon", "dmrecon"
            )
            self.scene2pset_fp = os.path.join(
                self.mve_apps_dp, "scene2pset", "scene2pset"
            )
            self.fssrecon_fp = os.path.join(
                self.mve_apps_dp, "fssrecon", "fssrecon"
            )
            self.meshclean_fp = os.path.join(
                self.mve_apps_dp, "meshclean", "meshclean"
            )

        assert os.path.isfile(self.make_scene_fp)
        assert os.path.isfile(self.dm_recon_fp)
        assert os.path.isfile(self.scene2pset_fp)
        assert os.path.isfile(self.fssrecon_fp)
        assert os.path.isfile(self.meshclean_fp)

    def get_point_cloud_with_scale_ply_fp(self):
        return os.path.join(self.workspace_folder, "mve_point_cloud.ply")

    def get_mesh_ply_fp(self):
        return os.path.join(self.workspace_folder, "mve_mesh.ply")

    def get_mesh_cleaned_ply_fp(self):
        return os.path.join(self.workspace_folder, "mve_mesh_cleaned.ply")

    def import_images_to_scene(self, image_idp):
        logger.info("import_images_to_scene: ...")
        make_scene_call = [
            self.make_scene_fp,
            "--images-only",
            image_idp,
            self.workspace_folder,
        ]
        logger.vinfo("make_scene_call", make_scene_call)
        subprocess.call(make_scene_call)

    def create_scene_from_sfm_result(self, sfm_fp_or_dp, downscale_level=None):
        # Input can be a nvm file or a colmap model folder
        assert self.workspace_folder is not None
        logger.info("Creating Scene: ...")
        logger.info("Input file/folder: " + sfm_fp_or_dp)
        logger.info("Output Path: " + self.workspace_folder)
        downscale_s_str = "-s" + str(downscale_level)
        make_scene_call = [
            self.make_scene_fp,
            downscale_s_str,
            sfm_fp_or_dp,
            self.workspace_folder,
        ]
        logger.vinfo("make_scene_call", make_scene_call)
        subprocess.call(make_scene_call)
        logger.info("Creating Scene: Done")

    def compute_sfm(self):
        logger.info("Compute SfM: ...")
        sfm_recon_call = [self.sfm_recon_fp, self.workspace_folder]
        logger.vinfo("sfm_recon_call", sfm_recon_call)
        subprocess.call(sfm_recon_call)
        logger.info("Compute SfM: Done")

    def compute_depth_maps(self, downscale_level=0):
        logger.info("compute_depth_maps: ...")

        downscale_s_str = "-s" + str(downscale_level)
        dm_recon_call = [
            self.dm_recon_fp,
            downscale_s_str,
            self.workspace_folder,
        ]
        logger.vinfo("dm_recon_call", dm_recon_call)
        subprocess.call(dm_recon_call)
        logger.info("compute_depth_maps: ...")

    def compute_dense_point_cloud_from_depth_maps(
        self,
        mve_point_cloud_ply_ofp,
        downscale_level=0,
        view_ids=None,
        fssr_output=True,
    ):
        logger.info("compute_dense_point_cloud_from_depth_maps: ...")
        assert os.path.splitext(mve_point_cloud_ply_ofp)[1] == ".ply"

        scene2pset_call = [self.scene2pset_fp]
        if fssr_output:
            downscale_F_str = "-F" + str(downscale_level)
            scene2pset_call.append(downscale_F_str)
        if view_ids is not None:
            view_id_str = "--views=" + ",".join(map(str, view_ids))
            scene2pset_call.append(view_id_str)
        scene2pset_call.append(self.workspace_folder)
        scene2pset_call.append(mve_point_cloud_ply_ofp)
        logger.vinfo("scene2pset_call", scene2pset_call)
        subprocess.call(scene2pset_call)

        logger.info("compute_dense_point_cloud_from_depth_maps: Done")

    def compute_fssr_mesh_from_point_cloud(
        self, mve_point_cloud_with_scale_ply_fp, mesh_ply_fp
    ):
        logger.info("compute_mesh_from_point_cloud: ...")
        subprocess.call(
            [self.fssrecon_fp, mve_point_cloud_with_scale_ply_fp, mesh_ply_fp]
        )
        logger.info("compute_mesh_from_point_cloud: Done")

    def compute_cleaned_mesh(
        self,
        mesh_ifp,
        mesh_ofp,
        threshold=1.0,
        component_size=1000,
        delete_color=True,
        delete_scale=True,
        delete_conf=True,
    ):
        logger.info("compute_cleaned_mesh: ...")
        clean_call = [
            self.meshclean_fp,
            # Threshold on the geometry confidence [1.0]
            # -t, --threshold=ARG
            "--threshold=" + str(threshold),
            # Minimum number of vertices per component [1000]
            # -c, --component-size=ARG
            "--component-size=" + str(component_size),
        ]
        if delete_color:
            clean_call += ["--delete-color"]
        if delete_scale:
            clean_call += ["--delete-scale"]
        if delete_conf:
            clean_call += ["--delete-conf"]

        clean_call += [mesh_ifp, mesh_ofp]

        subprocess.call(clean_call)
        logger.info("compute_cleaned_mesh: Done")

    def process_mve_create_scene_tasks(self, mve_create_scene_tasks):
        for mve_create_scene_task in mve_create_scene_tasks:

            logger.info("Perform Create Scene Task: ...")
            self.workspace_folder = mve_create_scene_task.mve_model_dir
            self.create_scene_from_sfm_result(
                mve_create_scene_task.model_file_path
            )
            logger.info("Perform Create Scene Task: Done")

            mve_point_cloud_ply_ofp = os.path.join(
                self.workspace_folder,
                mve_create_scene_task.mve_point_cloud_name,
            )

            self.compute_dense_point_cloud_from_depth_maps(
                mve_point_cloud_ply_ofp
            )