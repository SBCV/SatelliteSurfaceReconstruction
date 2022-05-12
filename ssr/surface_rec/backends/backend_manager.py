from ssr.surface_rec.backends.mesh_backend import MeshingBackends
from ssr.surface_rec.backends.decimation_backend import DecimationBackends
from ssr.surface_rec.backends.texturing_backend import TexturingBackends
from ssr.utility.logging_extension import logger


class BackendManager:
    def __init__(
        self,
        meshing_backends=None,
        texturing_backends=None,
        decimation_backends=None,
    ):

        if meshing_backends is None:
            self.meshing_backends = []
        else:
            self._check_meshing_backends(meshing_backends)
            self.meshing_backends = meshing_backends

        if decimation_backends is None:
            self.decimation_backends = []
        else:
            self._check_decimation_backends(decimation_backends)
            self.decimation_backends = decimation_backends

        if texturing_backends is None:
            self.texturing_backends = []
        else:
            self._check_texturing_backends(texturing_backends)
            self.texturing_backends = texturing_backends

    @staticmethod
    def _check_meshing_backends(meshing_backends):
        valid_backends = [
            MeshingBackends.colmap_poisson.name,
            MeshingBackends.colmap_delaunay.name,
            MeshingBackends.openmvs.name,
            MeshingBackends.mve_fssr.name,
            MeshingBackends.mve_gdmr.name,
        ]
        for meshing_backend in meshing_backends:
            if not meshing_backend in valid_backends:
                logger.vinfo("meshing_backend", meshing_backend)
                logger.vinfo("valid_backends", valid_backends)
                assert False

    @staticmethod
    def _check_decimation_backends(decimation_backends):
        valid_backends = [
            DecimationBackends.meshlab.name,
            DecimationBackends.openmvs.name,
        ]
        for decimation_backend in decimation_backends:
            if not decimation_backend in valid_backends:
                logger.vinfo("decimation_backend", decimation_backend)
                logger.vinfo("decimation_backends", decimation_backends)
                assert False

    @staticmethod
    def _check_texturing_backends(texturing_backends):
        valid_backends = [
            TexturingBackends.openmvs.name,
            TexturingBackends.mve.name,
        ]
        for texturing_backend in texturing_backends:
            if not texturing_backend in valid_backends:
                logger.vinfo("texturing_backend", texturing_backend)
                logger.vinfo("texturing_backends", texturing_backends)
                assert False

    def set_meshing_backends(self, meshing_backend_str_list):
        meshing_backends = MeshingBackends.convert_str_to_backend(
            meshing_backend_str_list
        )
        self._check_meshing_backends(meshing_backends)
        self.meshing_backends = meshing_backends

    def set_decimation_backends(self, decimation_backend_str_list):
        decimation_backends = DecimationBackends.convert_str_to_backend(
            decimation_backend_str_list
        )
        self._check_decimation_backends(decimation_backends)
        self.decimation_backends = decimation_backends

    def set_texturing_backends(self, texturing_backend_str_list):
        texturing_backends = TexturingBackends.convert_str_to_backend(
            texturing_backend_str_list
        )
        self._check_texturing_backends(texturing_backends)
        self.texturing_backends = texturing_backends
