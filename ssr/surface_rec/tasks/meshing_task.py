from ssr.surface_rec.tasks.task import Task


class MeshingTask(Task):
    def __init__(
        self,
        colmap_idp,
        mesh_odp,
        mesh_ply_ofn,
        plain_mesh_ply_ofn,
        meshing_backend,
        decimation_backends,
    ):

        self.__dict__.update(locals())
        # delete self, since it is redundant and a circular reference
        del self.self
