import subprocess


def to_shell_str(call_list):
    return " ".join(call_list)


def print_call(call_list):
    print(to_shell_str(call_list))


def run_vissat_as_subprocess(config_fp, vissat_stereo_pipeline_fp, python_fp):
    extract_call = [python_fp, vissat_stereo_pipeline_fp]
    extract_call += ["--config_file", config_fp]
    print_call(extract_call)
    subprocess.call(extract_call)


if __name__ == "__main__":
    config_fp = "/path/to/vissat_config.json"
    python_fp = "/path/to/bin/python3"
    # https://github.com/Kai-46/VisSatSatelliteStereo/blob/master/stereo_pipeline.py
    vissat_stereo_pipeline_fp = (
        "/path/to/VisSatSatelliteStereo/stereo_pipeline.py"
    )
    run_vissat_as_subprocess(config_fp, vissat_stereo_pipeline_fp, python_fp)
