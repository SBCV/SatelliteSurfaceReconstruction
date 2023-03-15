import os
import dill
import tempfile

from ssr.utility.logging_extension import logger


class PythonCache(object):
    def __init__(self):
        self.tmp_dir = tempfile.gettempdir()

    def get_cached_result(self, callback, params, unique_id_or_path):

        if type(unique_id_or_path) == int:
            cache_fp = os.path.join(self.tmp_dir, str(unique_id_or_path) + ".cache")
        elif type(unique_id_or_path) == str:
            cache_fp = unique_id_or_path
        else:
            assert False

        if os.path.isfile(cache_fp):
            logger.info("Reading data from dill cache")
            with open(cache_fp, "rb") as file:
                result = dill.load(file)
        else:
            logger.info("Reading data from txt reconstruction")
            with open(cache_fp, "wb") as file:
                result = callback(*params)
                dill.dump(result, file)
        return result
