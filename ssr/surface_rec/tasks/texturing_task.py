from ssr.surface_rec.tasks.task import Task


class TexturingTask(Task):
    def __init__(self, colmap_idp, mesh_ifp, textured_mesh_odp, texturing_backend):

        self.__dict__.update(locals())
        # delete self, since it is redundant and a circular reference
        del self.self
