import os

from ssr.config.ssr_config import SSRConfig
from ssr.surface_rec.backends.mesh_backend import (
    MeshingBackends,
)
from ssr.surface_rec.backends.texturing_backend import (
    TexturingBackends,
)
from ssr.surface_rec.tasks.task_manager import (
    TaskManager,
)
from ssr.surface_rec.meshing.meshing import MeshingStep

from ssr.surface_rec.surface.texturing import TexturingStep


from ssr.utility.logging_extension import logger
from ssr.utility.os_extension import mkdir_safely


class SurfaceReconstructionPipeline:
    def __init__(self, pm, bm):
        # path manager
        self.pm = pm
        # backend manager
        self.bm = bm
        # task manager
        self.tm = TaskManager(pm, bm)

        self.ssr_config = SSRConfig.get_instance()

    def run(self, reconstruct_mesh, texture_mesh, lazy=True):

        meshing_tasks = self.tm.detect_meshing_tasks(reconstruct_mesh)
        if meshing_tasks:
            mkdir_safely(self.pm.surface_workspace_dp)
            mkdir_safely(self.pm.mesh_workspace_dp)
        for meshing_task in meshing_tasks:
            self.process_meshing_task(meshing_task, lazy)

        texturing_tasks = self.tm.detect_texturing_tasks(texture_mesh)
        for texturingn_task in texturing_tasks:
            self.process_texturing_task(texturingn_task, lazy)

    def process_meshing_task(self, meshing_task, lazy):
        mesh_ply_ofn = meshing_task.mesh_ply_ofn
        plain_mesh_ply_ofn = meshing_task.plain_mesh_ply_ofn
        logger.vinfo("mesh_ply_ofn", mesh_ply_ofn)

        if meshing_task.meshing_backend == MeshingBackends.colmap_poisson:
            mkdir_safely(meshing_task.mesh_odp)
            MeshingStep.compute_mesh_with_colmap(
                meshing_task.colmap_idp,
                meshing_task.mesh_odp,
                mesh_ply_ofn,
                plain_mesh_ply_ofn,
                "poisson_mesher",
                poisson_trim_thresh=10,
                lazy=lazy,
            )
        elif meshing_task.meshing_backend == MeshingBackends.colmap_delaunay:
            mkdir_safely(meshing_task.mesh_odp)
            MeshingStep.compute_mesh_with_colmap(
                meshing_task.colmap_idp,
                meshing_task.mesh_odp,
                mesh_ply_ofn,
                plain_mesh_ply_ofn,
                "delaunay_mesher",
                lazy=lazy,
            )
        elif meshing_task.meshing_backend == MeshingBackends.openmvs:
            mkdir_safely(meshing_task.mesh_odp)
            MeshingStep.compute_mesh_with_openmvs(
                meshing_task.colmap_idp,
                meshing_task.mesh_odp,
                mesh_ply_ofn,
                plain_mesh_ply_ofn,
                lazy=lazy,
            )
        elif meshing_task.meshing_backend == MeshingBackends.mve_fssr:
            MeshingStep.compute_mesh_with_mve(
                meshing_task.colmap_idp,
                meshing_task.mesh_odp,
                mesh_ply_ofn,
                plain_mesh_ply_ofn,
                meshing_algo="fssr",
                lazy=lazy,
            )
        elif meshing_task.meshing_backend == MeshingBackends.mve_gdmr:
            MeshingStep.compute_mesh_with_mve(
                meshing_task.colmap_idp,
                meshing_task.mesh_odp,
                mesh_ply_ofn,
                plain_mesh_ply_ofn,
                meshing_algo="gdmr",
                lazy=lazy,
            )
        else:
            assert False

    def process_texturing_task(self, texturing_task, lazy):
        # Ensure that "<parent_folder>/surface" exists
        mkdir_safely(
            os.path.dirname(os.path.dirname(texturing_task.textured_mesh_odp))
        )
        if texturing_task.texturing_backend == TexturingBackends.openmvs:
            TexturingStep.compute_texturing_with_openmvs(
                texturing_task.colmap_idp, texturing_task.textured_mesh_odp
            )
        elif texturing_task.texturing_backend == TexturingBackends.mve:
            TexturingStep.compute_texturing_with_mve(
                texturing_task.colmap_idp,
                texturing_task.mesh_ifp,
                texturing_task.textured_mesh_odp,
            )
        else:
            assert False
