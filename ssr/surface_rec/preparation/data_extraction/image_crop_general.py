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


# cut the AOI out of the big satellite image

from lib.rpc_model import RPCModel
from lib.gen_grid import gen_grid
from lib.check_bbx import check_bbx

from ssr.gdal_utility.translation import perform_translation
from ssr.surface_rec.preparation.data_extraction.tone_map_general import (
    tone_map_hdr_to_ldr_general,
)
from ssr.surface_rec.preparation.data_extraction.parse_meta_msi import (
    parse_meta_msi,
)

import utm
import json
import numpy as np
import shutil
from lib.blank_ratio import blank_ratio
import multiprocessing
import glob
import dateutil.parser
import os
import logging


def crop_ntf_general(
    in_ntf,
    hdr_img_ofp,
    ntf_size=None,
    bbx_size=None,
    bands=None,
    ot="UInt16",
    scale_params=None,
    remove_aux_file=False,
):

    # Works for PAN and MSI images

    perform_translation(
        in_ntf,
        hdr_img_ofp,
        ntf_size,
        bbx_size,
        bands,
        ot,
        scale_params,
        remove_aux_file,
    )

    logging.info("png image to save: {}".format(hdr_img_ofp))


def image_crop_worker_general(
    ntf_file,
    xml_file,
    current_idx,
    total_cnt,
    utm_bbx_file,
    out_dir,
    result_file,
    ift,
    oft="png",
    remove_aux_file=False,
    apply_tone_mapping=True,
    joint_tone_mapping=True,
):
    with open(utm_bbx_file) as fp:
        utm_bbx = json.load(fp)
    ul_easting = utm_bbx["ul_easting"]
    ul_northing = utm_bbx["ul_northing"]
    lr_easting = utm_bbx["lr_easting"]
    lr_northing = utm_bbx["lr_northing"]
    zone_number = utm_bbx["zone_number"]
    alt_min = utm_bbx["alt_min"]
    alt_max = utm_bbx["alt_max"]

    northern = True if utm_bbx["hemisphere"] == "N" else False
    ul_lat, ul_lon = utm.to_latlon(
        ul_easting, ul_northing, zone_number, northern=northern
    )
    lr_lat, lr_lon = utm.to_latlon(
        lr_easting, lr_northing, zone_number, northern=northern
    )

    lat_points = np.array([ul_lat, lr_lat])
    lon_points = np.array([ul_lon, lr_lon])
    alt_points = np.array([alt_min, alt_max])
    xx_lat, yy_lon, zz_alt = gen_grid(lat_points, lon_points, alt_points)

    pid = os.getpid()
    effective_file_list = []
    logging.info(
        "process {}, cropping {}/{}, ntf: {}".format(
            pid, current_idx, total_cnt, ntf_file
        )
    )
    try:
        meta_dict = parse_meta_msi(xml_file)
        # check whether the image is too cloudy
        cloudy_thres = 0.5
        if meta_dict["cloudCover"] > cloudy_thres:
            logging.warning(
                "discarding this image because of too many clouds, cloudy level: {}, ntf: {}".format(
                    meta_dict["cloudCover"], ntf_file
                )
            )
            return

        # compute the bounding box
        rpc_model = RPCModel(meta_dict)
        col, row = rpc_model.projection(xx_lat, yy_lon, zz_alt)

        ul_col = int(np.round(np.min(col)))
        ul_row = int(np.round(np.min(row)))
        width = int(np.round(np.max(col))) - ul_col + 1
        height = int(np.round(np.max(row))) - ul_row + 1

        # check whether the bounding box lies in the image
        ntf_width = meta_dict["width"]
        ntf_height = meta_dict["height"]
        intersect, _, overlap = check_bbx(
            (0, 0, ntf_width, ntf_height), (ul_col, ul_row, width, height)
        )
        overlap_thres = 0.8
        if overlap < overlap_thres:
            logging.warning(
                "discarding this image due to small coverage of target area, overlap: {}, ntf: {}".format(
                    overlap, ntf_file
                )
            )
            return

        ul_col, ul_row, width, height = intersect

        # crop ntf
        idx1 = ntf_file.rfind("/")
        idx2 = ntf_file.rfind(".")
        base_name = ntf_file[idx1 + 1 : idx2]
        out_png = os.path.join(
            out_dir, "{}:{:04d}:{}.{}".format(pid, current_idx, base_name, oft)
        )

        if ift.lower() == "pan":
            bands = None
        elif ift.lower() == "msi":
            bands = [
                meta_dict["red_band_idx"],
                meta_dict["green_band_idx"],
                meta_dict["blue_band_idx"],
            ]
        else:
            assert False

        # ======================================
        # Use QGIS to examine the PNG result
        # (i.e. color range of the created file)
        # ======================================
        crop_ntf_general(
            in_ntf=ntf_file,
            hdr_img_ofp=out_png,
            ntf_size=(ntf_width, ntf_height),
            bbx_size=(ul_col, ul_row, width, height),
            bands=bands,
            remove_aux_file=remove_aux_file,
        )

        if apply_tone_mapping:
            if oft.lower() == "png":
                tone_map_hdr_to_ldr_general(
                    out_png, out_png, joint_tone_mapping
                )
            else:
                # If we do not perform tone mapping here, the ratio test below
                # would remove many images!
                logging.error("Tone mapping not implemented for GTiff format")
                assert False
        else:
            logging.warning("No tone mapping applied !!!")

        ratio = blank_ratio(out_png)
        if ratio > 0.2:
            logging.warning(
                "discarding this image due to large portion of black pixels, ratio: {}, ntf: {}".format(
                    ratio, ntf_file
                )
            )
            os.remove(out_png)
            return

        # save meta_dict
        # subtract the cutting offset here
        rpc_dict = meta_dict["rpc"]
        rpc_dict["colOff"] = rpc_dict["colOff"] - ul_col
        rpc_dict["rowOff"] = rpc_dict["rowOff"] - ul_row
        meta_dict["rpc"] = rpc_dict
        # modify width, height
        meta_dict["width"] = width
        meta_dict["height"] = height
        # change datetime object to string
        meta_dict["capTime"] = meta_dict["capTime"].isoformat()

        meta_dict["ul_col_original"] = ul_col
        meta_dict["ul_row_original"] = ul_row

        out_json = os.path.join(
            out_dir, "{}:{:04d}:{}.json".format(pid, current_idx, base_name)
        )
        with open(out_json, "w") as fp:
            json.dump(meta_dict, fp, indent=2)
        effective_file_list.append((out_png, out_json))

    finally:
        with open(result_file, "w") as fp:
            json.dump(effective_file_list, fp, indent=2)


def image_crop_general(
    work_dir,
    ift,
    oft,
    execute_parallel,
    remove_aux_file,
    apply_tone_mapping,
    joint_tone_mapping,
):
    cleaned_data_dir = os.path.join(work_dir, "cleaned_data")
    ntf_list = glob.glob("{}/*.NTF".format(cleaned_data_dir))
    xml_list = [item[:-4] + ".XML" for item in ntf_list]

    # create a tmp dir
    tmp_dir = os.path.join(work_dir, "tmp")
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    result_file_list = []
    cnt = len(ntf_list)
    for i in range(cnt):
        ntf_file = ntf_list[i]
        xml_file = xml_list[i]

        utm_bbx_file = os.path.join(work_dir, "aoi.json")
        out_dir = tmp_dir
        result_file = os.path.join(
            tmp_dir, "image_crop_result_{}.json".format(i)
        )
        result_file_list.append(result_file)

        if execute_parallel:
            pool.apply_async(
                image_crop_worker_general,
                (
                    ntf_file,
                    xml_file,
                    i,
                    cnt,
                    utm_bbx_file,
                    out_dir,
                    result_file,
                    ift,
                    oft,
                    remove_aux_file,
                    apply_tone_mapping,
                    joint_tone_mapping,
                ),
            )
        else:
            image_crop_worker_general(
                ntf_file,
                xml_file,
                i,
                cnt,
                utm_bbx_file,
                out_dir,
                result_file,
                ift,
                oft,
                remove_aux_file,
                apply_tone_mapping,
                joint_tone_mapping,
            )

    pool.close()
    pool.join()

    # now try to merge the cropping result
    all_files = []
    for result_file in result_file_list:
        with open(result_file) as fp:
            all_files += json.load(fp)

    # sort the files in chronological order
    cap_times = {}
    sensor_ids = {}
    for img_file, meta_file in all_files:
        with open(meta_file) as fp:
            meta_dict = json.load(fp)
        cap_times[img_file] = dateutil.parser.parse(meta_dict["capTime"])
        sensor_ids[img_file] = meta_dict["sensor_id"]
    all_files = sorted(all_files, key=lambda x: cap_times[x[0]])

    # copy data to target dir and prepend with increasing index
    images_subdir = os.path.join(work_dir, "images")
    aux_xml_subdir = os.path.join(work_dir, "aux_xml")
    metas_subdir = os.path.join(work_dir, "metas")
    for subdir in [images_subdir, metas_subdir, aux_xml_subdir]:
        if os.path.exists(subdir):
            shutil.rmtree(subdir)
        os.mkdir(subdir)

    for i in range(len(all_files)):
        img_file, meta_file = all_files[i]
        idx = img_file.rfind(":")
        sensor = sensor_ids[img_file]
        time = img_file[idx + 1 : idx + 8]
        target_img_name = "{:04d}_{}_{}_{}".format(
            i, sensor, time, img_file[idx + 8 :]
        )

        idx = meta_file.rfind(":")
        time = img_file[idx + 1 : idx + 8]
        target_xml_name = "{:04d}_{}_{}_{}".format(
            i, sensor, time, meta_file[idx + 8 :]
        )

        shutil.copyfile(img_file, os.path.join(images_subdir, target_img_name))
        shutil.copyfile(meta_file, os.path.join(metas_subdir, target_xml_name))

        if not remove_aux_file:
            aux_xml_file = img_file + ".aux.xml"
            target_aux_xml_name = target_img_name + ".aux.xml"
            shutil.copyfile(
                aux_xml_file, os.path.join(aux_xml_subdir, target_aux_xml_name)
            )

    # remove tmp_dir
    shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    pass
