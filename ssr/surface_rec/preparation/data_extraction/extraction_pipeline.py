#  ===============================================================================================================
#  Copyright (c) 2019, Cornell University. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that
#  the following conditions are met:
#
#      * Redistributions of source code must retain the above copyright otice, this list of conditions and
#        the following disclaimer.
#
#      * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
#        the following disclaimer in the documentation and/or other materials provided with the distribution.
#
#      * Neither the name of Cornell University nor the names of its contributors may be used to endorse or
#        promote products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#  TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
#  OF SUCH DAMAGE.
#
#  Author: Kai Zhang (kz298@cornell.edu)
#
#  The research is based upon work supported by the Office of the Director of National Intelligence (ODNI),
#  Intelligence Advanced Research Projects Activity (IARPA), via DOI/IBC Contract Number D17PC00287.
#  The U.S. Government is authorized to reproduce and distribute copies of this work for Governmental purposes.
#  ===============================================================================================================


import os
import json
from ssr.surface_rec.preparation.data_extraction.clean_data_general import (
    clean_data_general,
)
from ssr.surface_rec.preparation.data_extraction.image_crop_general import (
    image_crop_general,
)
import shutil
import logging
from lib.timer import Timer
from lib.logger import GlobalLogger
import utm
from datetime import datetime


class ExtractionPipeline(object):
    def __init__(self, config_file):
        with open(config_file) as fp:
            self.config = json.load(fp)

        # make work_dir
        if not os.path.exists(self.config["work_dir"]):
            os.mkdir(self.config["work_dir"])
        logs_subdir = os.path.join(self.config["work_dir"], "logs")
        if not os.path.exists(logs_subdir):
            os.mkdir(logs_subdir)

        self.logger = GlobalLogger()

    def run(
        self,
        ift,
        oft,
        execute_parallel,
        remove_aux_file,
        apply_tone_mapping,
        joint_tone_mapping,
    ):
        self.write_aoi()

        per_step_time = []  # (whether to run, step name, time in minutes)

        if self.config["steps_to_run"]["clean_data"]:
            start_time = datetime.now()
            self.clean_data_general(ift)
            duration = (datetime.now() - start_time).total_seconds() / 60.0  # minutes
            per_step_time.append((True, "clean_data", duration))
            print("step clean_data:\tfinished in {} minutes".format(duration))
        else:
            per_step_time.append((False, "clean_data", 0.0))
            print("step clean_data:\tskipped")

        if self.config["steps_to_run"]["crop_image"]:
            start_time = datetime.now()
            self.run_crop_image_general(
                ift,
                oft,
                execute_parallel,
                remove_aux_file,
                apply_tone_mapping,
                joint_tone_mapping,
            )
            duration = (datetime.now() - start_time).total_seconds() / 60.0  # minutes
            per_step_time.append((True, "crop_image", duration))
            print("step crop_image:\tfinished in {} minutes".format(duration))
        else:
            per_step_time.append((False, "crop_image", 0.0))
            print("step crop_image:\tskipped")

        with open(os.path.join(self.config["work_dir"], "runtime.txt"), "w") as fp:
            fp.write("step_name, status, duration (minutes)\n")
            total = 0.0
            for (has_run, step_name, duration) in per_step_time:
                if has_run:
                    fp.write("{}, success, {}\n".format(step_name, duration))
                else:
                    fp.write("{}, skipped\n".format(step_name))
                total += duration
            fp.write("\ntotal: {} minutes\n".format(total))
            print("total:\t{} minutes".format(total))

    def write_aoi(self):
        # write aoi.json
        bbx_utm = self.config["bounding_box"]
        zone_number = bbx_utm["zone_number"]
        hemisphere = bbx_utm["hemisphere"]
        ul_easting = bbx_utm["ul_easting"]
        ul_northing = bbx_utm["ul_northing"]
        lr_easting = ul_easting + bbx_utm["width"]
        lr_northing = ul_northing - bbx_utm["height"]

        # compute a lat_lon bbx
        corners_easting = [ul_easting, lr_easting, lr_easting, ul_easting]
        corners_northing = [ul_northing, ul_northing, lr_northing, lr_northing]
        corners_lat = []
        corners_lon = []
        northern = True if hemisphere == "N" else False
        for i in range(4):
            lat, lon = utm.to_latlon(
                corners_easting[i],
                corners_northing[i],
                zone_number,
                northern=northern,
            )
            corners_lat.append(lat)
            corners_lon.append(lon)
        lat_min = min(corners_lat)
        lat_max = max(corners_lat)
        lon_min = min(corners_lon)
        lon_max = max(corners_lon)

        aoi_dict = {
            "zone_number": zone_number,
            "hemisphere": hemisphere,
            "ul_easting": ul_easting,
            "ul_northing": ul_northing,
            "lr_easting": lr_easting,
            "lr_northing": lr_northing,
            "width": bbx_utm["width"],
            "height": bbx_utm["height"],
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lon_min": lon_min,
            "lon_max": lon_max,
            "alt_min": self.config["alt_min"],
            "alt_max": self.config["alt_max"],
        }

        with open(os.path.join(self.config["work_dir"], "aoi.json"), "w") as fp:
            json.dump(aoi_dict, fp, indent=2)

    def clean_data_general(self, ift):
        dataset_dir = self.config["dataset_dir"]
        work_dir = self.config["work_dir"]

        # set log file and timer
        log_file = os.path.join(work_dir, "logs/log_clean_data.txt")
        self.logger.set_log_file(log_file)
        # create a local timer
        local_timer = Timer("Data cleaning Module")
        local_timer.start()

        # clean data
        cleaned_data_dir = os.path.join(work_dir, "cleaned_data")
        if os.path.exists(cleaned_data_dir):  # remove cleaned_data_dir
            shutil.rmtree(cleaned_data_dir)
        os.mkdir(cleaned_data_dir)

        # check if dataset_dir is a list or tuple
        if not (isinstance(dataset_dir, list) or isinstance(dataset_dir, tuple)):
            dataset_dir = [
                dataset_dir,
            ]
        clean_data_general(dataset_dir, cleaned_data_dir, ift=ift)

        # stop local timer
        local_timer.mark("Data cleaning done")
        logging.info(local_timer.summary())

    def run_crop_image_general(
        self,
        ift,
        oft,
        execute_parallel,
        remove_aux_file,
        apply_tone_mapping,
        joint_tone_mapping,
    ):
        work_dir = self.config["work_dir"]

        # set log file
        log_file = os.path.join(work_dir, "logs/log_crop_image.txt")
        self.logger.set_log_file(log_file)

        # create a local timer
        local_timer = Timer("Image cropping module")
        local_timer.start()

        # crop image and tone map
        image_crop_general(
            work_dir,
            ift,
            oft,
            execute_parallel,
            remove_aux_file,
            apply_tone_mapping,
            joint_tone_mapping,
        )

        # stop local timer
        local_timer.mark("image cropping done")
        logging.info(local_timer.summary())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Satellite Stereo")
    parser.add_argument("--config_file", type=str, help="configuration file")

    args = parser.parse_args()
    pipeline = ExtractionPipeline(args.config_file)
    ift = "pan"
    oft = "png"
    pipeline.run(ift, oft)
