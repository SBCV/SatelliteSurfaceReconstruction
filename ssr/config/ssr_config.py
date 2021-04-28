import os
import json
import configparser
from ssr.utility.logging_extension import logger


_config = None


class SSRConfig:

    default_section = "DEFAULT"
    comment_symbol = "#"

    @staticmethod
    def get_instance():
        assert _config is not None
        return _config

    @staticmethod
    def set_instance(config):
        global _config
        _config = config

    def __init__(self, config_fp, working_file_suffix=None):

        self.config_fp = config_fp
        self.config = configparser.RawConfigParser()

        if not os.path.isfile(self.config_fp):
            abs_path = os.path.abspath(os.path.dirname(self.config_fp))
            if not os.path.isdir(abs_path):
                logger.vinfo("abs_path", abs_path)
                assert False  # config folder missing
            open(self.config_fp, "a").close()
        else:
            self.config.read(self.config_fp)

        if working_file_suffix is not None:
            self.path_to_working_copy = self.config_fp + working_file_suffix
        else:
            self.path_to_working_copy = self.config_fp

    def add_option_value_pairs(self, pair_list, section=None):
        """
        :param tuple_list: ('option', 'Value')
        :return:
        """
        if section is None:
            section = SSRConfig.default_section
        elif not self.config.has_section(section):
            self.config.add_section(section)

        for pair in pair_list:
            option, value = pair
            self.config.set(section, option, value)

    @staticmethod
    def detect_missing_commas(list_str):
        repaired_string = list_str.replace('"\n"', '",\n"')
        return repaired_string

    @staticmethod
    def remove_appended_commas(list_str):
        repaired_string = list_str.replace('",\n]', '"\n]')
        return repaired_string

    def get_option_value(self, option, target_type, section=None):
        """
        :param section:
        :param option:
        :param target_type:
        :return:
        """
        if section is None:
            section = SSRConfig.default_section

        try:
            if target_type == list:
                option_str = self.config.get(section, option)
                option_str = SSRConfig.detect_missing_commas(option_str)
                option_str = SSRConfig.remove_appended_commas(option_str)
                result = json.loads(option_str)
            else:
                option_str = self.config.get(section, option)
                option_str = option_str.split("#")[0].rstrip()
                if (
                    target_type == bool
                ):  # Allow True/False bool values in addition to 1/0
                    result = (
                        option_str == "True"
                        or option_str == "T"
                        or option_str == "1"
                    )
                else:
                    result = target_type(option_str)

        except configparser.NoOptionError as NoOptErr:
            logger.info("ERROR: " + str(NoOptErr))
            logger.info("CONFIG FILE: " + self.config_fp)
            assert False  # Option Missing
        except:
            logger.info("option_str: " + str(option_str))
            raise

        return result

    def get_option_value_or_default_value(
        self, option, target_type, default_value, section=None
    ):
        if section is None:
            section = SSRConfig.default_section

        if self.config.has_option(section, option):
            result = self.get_option_value(
                option, target_type, section=section
            )
        else:
            result = default_value
            assert type(result) == target_type
        return result

    def get_option_value_or_None(self, option, target_type, section=None):
        if section is None:
            section = SSRConfig.default_section
        result = None
        if self.config.has_option(section, option):
            result = self.get_option_value(
                option, target_type, section=section
            )
        return result

    def log_option_value_pairs(self):
        for val in self.config.values():
            logger.info(val)

    def write_state_to_disc(self):
        with open(self.path_to_working_copy, "w") as configfile:
            self.config.write(configfile)


if __name__ == "__main__":

    logger.info("Main called")

    config = SSRConfig(config_fp="example.cfg")
    section_option_value_pairs = [
        ("option1", "125"),
        ("option2", "aaa"),
        ("option1", "222"),
        ("option3", "213"),
    ]
    config.add_option_value_pairs(
        section_option_value_pairs, section="Section1"
    )

    option_value_pairs = [("option5", "333"), ("option6", "555")]
    config.add_option_value_pairs(option_value_pairs)

    config.log_option_value_pairs()
    config.write_state_to_disc()

    some_number = config.get_option_value("option1", int, section="Section1")
    logger.info(some_number)
    logger.info(some_number + 3)

    some_number = config.get_option_value("option5", int)
    logger.info(some_number)
    logger.info(some_number + 3)
