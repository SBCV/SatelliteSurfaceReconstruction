import os
from ssr.surface_rec.tasks.meshing_task import (
    MeshingTask,
)
from ssr.surface_rec.tasks.reduction_task import (
    ReductionTask,
)
from ssr.surface_rec.tasks.refinement_task import (
    RefinementTask,
)
from ssr.surface_rec.tasks.texturing_task import (
    TexturingTask,
)
from ssr.surface_rec.backends.mesh_backend import (
    MeshingBackends,
)


class TaskManager:
    def __init__(self, pm, bm):
        """pm (path manager) and bm (backend manager)"""
        self.pm = pm
        self.bm = bm

    def detect_meshing_tasks(self, reconstruct_mesh):
        meshing_tasks = []
        if reconstruct_mesh:
            for meshing_backend in self.bm.meshing_backends:
                mesh_odp = os.path.join(self.pm.mesh_workspace_dp, meshing_backend)
                meshing_task = MeshingTask(
                    colmap_idp=self.pm.colmap_workspace_no_skew_dp,
                    mesh_odp=mesh_odp,
                    mesh_ply_ofn=self.pm.mesh_ply_ofn,
                    plain_mesh_ply_ofn=self.pm.plain_mesh_ply_ofn,
                    meshing_backend=meshing_backend,
                    decimation_backends=self.bm.decimation_backends,
                )
                meshing_tasks.append(meshing_task)
        return meshing_tasks

    def detect_reduction_tasks(self):
        reduction_tasks = []
        for meshing_backend in self.bm.meshing_backends:
            # Reduction only for: Colmap Poisson Meshes
            if meshing_backend == MeshingBackends.colmap_poisson.name:
                reduction_odp = os.path.join(self.pm.mesh_workspace_dp, meshing_backend)
                reduction_task = ReductionTask(
                    colmap_idp=self.pm.colmap_workspace_no_skew_dp,
                    mesh_odp=reduction_odp,
                )
                reduction_tasks.append(reduction_task)
            else:
                assert meshing_backend in [
                    MeshingBackends.colmap_delaunay.name,
                    MeshingBackends.openmvs.name,
                    MeshingBackends.mve_fssr.name,
                    MeshingBackends.mve_gdmr.name,
                ]
        return reduction_tasks

    def detect_refinement_tasks(self, refine_mesh):
        refinement_tasks = []
        if refine_mesh:
            for meshing_backend in self.bm.meshing_backends:
                refinement_odp = os.path.join(
                    self.pm.mesh_workspace_dp, meshing_backend.name
                )
                plain_mesh_ply_ofp = os.path.join(
                    refinement_odp, self.pm.plain_mesh_ply_ofn
                )
                plain_mesh_refined_ply_ofp = os.path.join(
                    refinement_odp, self.pm.plain_mesh_refined_ply_ofn
                )
                refinement_task = RefinementTask(
                    colmap_idp=self.pm.colmap_workspace_no_skew_dp,
                    ply_ifp=plain_mesh_ply_ofp,
                    ply_ofp=plain_mesh_refined_ply_ofp,
                )
                refinement_tasks.append(refinement_task)
        return refinement_tasks

    def detect_texturing_tasks(self, texture_mesh):
        texturing_tasks = []
        if texture_mesh:
            for meshing_backend in self.bm.meshing_backends:
                untextured_mesh_ifp = os.path.join(
                    self.pm.mesh_workspace_dp,
                    meshing_backend,
                    "plain_mesh.ply",
                )

                for texturing_backend in self.bm.texturing_backends:
                    textured_mesh_odp = os.path.join(
                        self.pm.texturing_workspace_dp,
                        texturing_backend,
                        meshing_backend,
                    )
                    texturing_task = TexturingTask(
                        colmap_idp=self.pm.colmap_workspace_no_skew_dp,
                        mesh_ifp=untextured_mesh_ifp,
                        textured_mesh_odp=textured_mesh_odp,
                        texturing_backend=texturing_backend,
                    )
                    texturing_tasks.append(texturing_task)
        return texturing_tasks
