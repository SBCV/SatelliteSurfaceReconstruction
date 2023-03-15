from enum import Enum


class MeshlabBackend:
    def __str__(self):
        return "MeshlabDecimationBackend"

    def __repr__(self):
        return self.__str__()


class OpenMVSBackend:
    def __str__(self):
        return "OpenMVSDecimationBackend"

    def __repr__(self):
        return self.__str__()


class DecimationBackends(Enum):
    meshlab = MeshlabBackend()
    openmvs = OpenMVSBackend()

    @classmethod
    def get_str_to_backend_map(cls):
        return {str(backend): backend for backend in cls}

    @classmethod
    def convert_str_to_backend(cls, backend_str_list):
        str_to_backend = cls.get_str_to_backend_map()
        backend_list = [str_to_backend[backend_str] for backend_str in backend_str_list]
        return backend_list
