import logging
import subprocess
import shlex


def run_gdal_cmd(cmd, disable_log=False, input=None):
    logging.info("logging run_cmd")
    if not disable_log:
        logging.info("Running subprocess: {}".format(cmd))

    try:
        process = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
        )

        if input is not None:
            # interacting with short-running subprocess
            output = process.communicate(input=input.encode())[0]
            if not disable_log:
                logging.info(output.decode())
            else:
                process.wait()
        else:
            # interacting with long-running subprocess
            if not disable_log:
                while True:
                    output = process.stdout.readline().decode()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        logging.info(output)
            else:
                process.wait()
    except (OSError, subprocess.CalledProcessError) as exception:
        logging.info("oh my goodness!")
        logging.error("Exception occured: {}, cmd: {}".format(exception, cmd))
        logging.error("Subprocess failed")
        exit(-1)
    else:
        if not disable_log:
            # no exception was raised
            logging.info("Subprocess finished")
