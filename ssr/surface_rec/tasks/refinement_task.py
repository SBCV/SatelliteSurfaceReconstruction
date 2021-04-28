from ssr.surface_rec.tasks.task import Task


class RefinementTask(Task):
    def __init__(self, colmap_idp, ply_ifp, ply_ofp):

        self.__dict__.update(locals())
        # delete self, since it is redundant and a circular reference
        del self.self
