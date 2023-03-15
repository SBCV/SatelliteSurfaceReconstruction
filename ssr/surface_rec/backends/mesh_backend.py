from enum import Enum


class BaseBackend:
    def __init__(self):
        self.name = "Base"
        self.suffix = "MeshBackend"

    def __str__(self):
        return self.name + self.suffix

    def __repr__(self):
        return self.__str__()


class ColmapMeshBackend(BaseBackend):
    def __init__(self, poisson):
        super().__init__()
        self.poisson = poisson
        if self.poisson:
            self.name = "ColmapPoisson"
        else:
            self.name = "ColmapDelaunay"


class OpenmvsMeshBackend(BaseBackend):
    def __init__(self):
        super().__init__()
        self.name = "Openmvs"


class MveMeshBackend(BaseBackend):
    def __init__(self, fssr):
        super().__init__()
        self.fssr = fssr
        if self.fssr:
            self.name = "MveFssr"
        else:
            self.name = "MveGDMR"


class MeshingBackends(Enum):
    colmap_delaunay = ColmapMeshBackend(poisson=False)
    colmap_poisson = ColmapMeshBackend(poisson=True)
    openmvs = OpenmvsMeshBackend()
    mve_fssr = MveMeshBackend(fssr=True)
    mve_gdmr = MveMeshBackend(fssr=False)

    @classmethod
    def get_str_to_backend_map(cls):
        return {str(backend): backend for backend in cls}

    @classmethod
    def convert_str_to_backend(cls, backend_str_list):
        str_to_backend = cls.get_str_to_backend_map()
        backend_list = [str_to_backend[backend_str] for backend_str in backend_str_list]
        return backend_list
