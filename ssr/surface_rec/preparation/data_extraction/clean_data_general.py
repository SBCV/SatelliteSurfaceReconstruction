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
import tarfile
import shutil
import unicodedata
import logging

# first find .NTF file, and extract order_id, prod_id, standard name
# then extract rpc file and preview image from the .tar file


def clean_image_info_general(file_name, ift):
    file_name = os.path.basename(file_name)
    # get order_id, prod_id
    if ift.lower() == "pan":
        idx = file_name.find("-P1BS-")
    elif ift.lower() == "msi":
        idx = file_name.find("-M1BS-")
    else:
        assert False
    order_id = file_name[idx + 6 : idx + 21]
    prod_id = file_name[idx + 6 : idx + 26]
    img_name = file_name[idx - 13 : idx + 26]
    return img_name, order_id, prod_id


def process_clean_data_item_general(item, dataset_dir, out_dir, tmp_dir, ift):
    logging.info("process_clean_data_item: ...")
    if item[-4:] == ".NTF" and os.path.exists(
        os.path.join(dataset_dir, "{}.tar".format(item[:-4]))
    ):
        logging.info("cleaning {}".format(item))
        img_name, order_id, prod_id = clean_image_info_general(item, ift)
        os.symlink(
            os.path.join(dataset_dir, item),
            os.path.join(out_dir, "{}.NTF".format(img_name)),
        )
        tar = tarfile.open(os.path.join(dataset_dir, "{}.tar".format(item[:-4])))
        tar.extractall(os.path.join(tmp_dir, img_name))

        subfolder = "DVD_VOL_1"
        for x in os.listdir(os.path.join(tmp_dir, img_name, order_id)):
            if "DVD_VOL" in x:
                subfolder = x
                break

        des_folder = os.path.join(tmp_dir, img_name, order_id, subfolder, order_id)

        if ift.lower() == "pan":
            suffix = "PAN"
        elif ift.lower() == "msi":
            suffix = "MUL"
        else:
            assert False

        rpc_file = os.path.join(
            des_folder,
            "{}_{}".format(prod_id, suffix),
            "{}.XML".format(img_name),
        )
        jpg_file = os.path.join(
            des_folder,
            "{}_{}".format(prod_id, suffix),
            "{}-BROWSE.JPG".format(img_name),
        )
        img_files = [rpc_file, jpg_file]
        for x in img_files:
            shutil.copy(x, out_dir)

        # remove control characters in the xml file
        rpc_file = os.path.join(out_dir, "{}.XML".format(img_name))
        with open(rpc_file, encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
        content = "".join([ch for ch in content if unicodedata.category(ch)[0] != "C"])
        with open(rpc_file, "w") as fp:
            fp.write(content)
        return True
    return False


def clean_data_general(dataset_dirs, out_dir, pairing=None, ift="PAN"):
    # out_dir must exist and be empty
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    dataset_dirs = [os.path.abspath(dataset_dir) for dataset_dir in dataset_dirs]
    logging.info("dataset path: {}".format(dataset_dirs))
    logging.info("will save files to folder: {}".format(out_dir))
    logging.info(
        "the standard format is: <7 char date><6 char time>-P1BS-<20 char product id>.NTF\n\n"
    )

    tmp_dir = os.path.join(out_dir, "tmp")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)

    cnt = 0
    if pairing is not None:
        logging.info("pairing: " + str(pairing))
        for p in pairing:
            pan_ntf = p[0]
            item = os.path.basename(pan_ntf)
            dataset_dir = os.path.dirname(pan_ntf)
            if process_clean_data_item_general(
                item, dataset_dir, out_dir, tmp_dir, ift
            ):
                cnt += 1
    else:
        logging.info("pairing: " + str(pairing))
        for dataset_dir in sorted(dataset_dirs):
            for item in sorted(os.listdir(dataset_dir)):
                # if 'WV03' not in item:  # only select 'WV03' satellite images
                #     continue
                if process_clean_data_item_general(
                    item, dataset_dir, out_dir, tmp_dir, ift
                ):
                    cnt += 1

    logging.info("processed {} items in total".format(cnt))
    # remove tmp_dir
    shutil.rmtree(tmp_dir)


if __name__ == "__main__":

    def main():
        dataset_dir = "/data2/kz298/core3d_pan/jacksonville"
        out_dir = os.path.join(dataset_dir, "cleaned_data")
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        clean_data_general(dataset_dir, out_dir)

    main()
