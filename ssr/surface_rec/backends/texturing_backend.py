from enum import Enum


class OpenmvsTexturingBackend:
    def __str__(self):
        return "OpenmvsTexturingBackend"

    def __repr__(self):
        return self.__str__()


class MveTexturingBackend:
    def __str__(self):
        return "MveTexturingBackend"

    def __repr__(self):
        return self.__str__()


# class Open3dTexturingBackend:
#     def __str__(self):
#         return "Open3dTexturingBackend"
#
#     def __repr__(self):
#         return self.__str__()


class TexturingBackends(Enum):
    openmvs = OpenmvsTexturingBackend()
    mve = MveTexturingBackend()
    # open3d = Open3dTexturingBackend()

    @classmethod
    def get_str_to_backend_map(cls):
        return {str(backend): backend for backend in cls}

    @classmethod
    def convert_str_to_backend(cls, backend_str_list):
        str_to_backend = cls.get_str_to_backend_map()
        backend_list = [
            str_to_backend[backend_str] for backend_str in backend_str_list
        ]
        return backend_list
