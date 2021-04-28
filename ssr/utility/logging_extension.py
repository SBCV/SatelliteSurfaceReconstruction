import logging as standard_logging

standard_logging.basicConfig(level=standard_logging.INFO)
standard_logger = standard_logging.getLogger()


class CustomLogger:
    def info(self, param, log=True):
        if log:
            standard_logger.info(param)

    def debug(self, param, log=True):
        if log:
            standard_logger.debug(param)

    def warning(self, param, log=True):
        if log:
            standard_logger.warning(param)

    def vinfo(self, some_str, some_var, log=True):
        if log:
            assert type(some_str) is str
            if some_var is None:
                some_var = "None"
            standard_logger.info(some_str + ": " + str(some_var))


logger = CustomLogger()
