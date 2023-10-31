import os.path
import shutil
from collections import defaultdict

from ssr.utility.os_extension import get_file_paths_in_dir, mkdir_safely


def main(track_3_rgb_idp, track_3_truth_idp, root_odp):
    tif_ifp_list = get_file_paths_in_dir(track_3_rgb_idp, ext=".tif")
    # Sites are defined by 3 letters followed by 3 digits (e.g. JAX_004)
    location_id_str_to_tif_list = defaultdict(list)
    for tif_ifp in tif_ifp_list:
        fn = os.path.basename(tif_ifp)
        location_id_str = fn[0:7]
        assert fn[7] == "_"
        location_id_str_to_tif_list[location_id_str].append(tif_ifp)

    mkdir_safely(root_odp)
    for location_id_str, tif_list in location_id_str_to_tif_list.items():
        print(f" === {location_id_str} === ")

        dsm_txt_fn = f"{location_id_str}_DSM.txt"
        dsm_txt_ifp = os.path.join(track_3_truth_idp, dsm_txt_fn)

        odp = os.path.join(root_odp, location_id_str)
        mkdir_safely(odp)

        dsm_txt_ofp = os.path.join(odp, dsm_txt_fn)
        shutil.copyfile(dsm_txt_ifp, dsm_txt_ofp)

        for tif_ifp in tif_list:
            tif_fn = os.path.basename(tif_ifp)
            tif_ofp = os.path.join(odp, tif_fn)
            shutil.copyfile(tif_ifp, tif_ofp)


if __name__ == "__main__":

    track_3_rgb_idp = "/path/to/Train-Track3-RGB-1/Track3-RGB-1"
    track_3_truth_idp = "/path/to/Train-Track3-Truth/Track3-Truth"
    root_odp = "/path/to/dataset_track3_prepared"

    main(track_3_rgb_idp, track_3_truth_idp, root_odp)
