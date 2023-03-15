import os
import subprocess
import platform
from ssr.utility.logging_extension import logger
from ssr.config.ssr_config import SSRConfig


class MVETexrecon:

    # https://www.gcc.tu-darmstadt.de/home/proj/texrecon/index.en.jsp

    def __init__(self):
        self.ssr_config = SSRConfig.get_instance()
        self.texrecon_apps_dp = self.ssr_config.texrecon_apps_dp
        assert self.texrecon_apps_dp is not None
        if platform.system() == "Windows":
            self.texrecon_executable = os.path.join(
                self.texrecon_apps_dp, "texrecon.exe"
            )
        else:
            self.texrecon_executable = os.path.join(
                self.texrecon_apps_dp, "texrecon", "texrecon"
            )

    def create_textured_mesh(
        self,
        mve_scene_idp,
        untextured_mesh_ifp,
        texture_odp,
        occlusion_handling=True,
    ):
        logger.vinfo("texture_odp", texture_odp)
        current_working_dir = os.getcwd()
        if not os.path.isdir(texture_odp):
            os.makedirs(texture_odp)
        # Change the directory, since texrecon creates the files in the current
        # directory
        os.chdir(texture_odp)
        logger.vinfo("texture_odp", texture_odp)

        options = []
        options += ["--keep_unseen_faces"]
        if occlusion_handling:
            # Only the following options created reasonable results:
            options += ["--data_term=area", "--outlier_removal=gauss_damping"]

        texturing_call = (
            [self.texrecon_executable]
            + options
            + [
                mve_scene_idp + "::undistorted",
                untextured_mesh_ifp,
                "textured",
            ]
        )
        logger.vinfo("texturing_call", texturing_call)
        subprocess.call(texturing_call)

        # reset the working directory
        os.chdir(current_working_dir)

    def process_mve_create_textured_mesh_tasks(self, mve_create_textured_mesh_tasks):
        for mve_create_textured_mesh_task in mve_create_textured_mesh_tasks:
            self.create_textured_mesh(
                mve_create_textured_mesh_task.mve_scene_path,
                mve_create_textured_mesh_task.untextured_mesh_path_and_name,
                mve_create_textured_mesh_task.output_dir,
            )
