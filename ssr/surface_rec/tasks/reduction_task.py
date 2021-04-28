from ssr.surface_rec.tasks.task import Task


class ReductionTask(Task):
    def __init__(self, colmap_idp, mesh_odp):

        self.__dict__.update(locals())
        # delete self, since it is redundant and a circular reference
        del self.self
