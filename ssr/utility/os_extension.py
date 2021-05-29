import os
import shutil
import re


def delete_files_in_dir(
    idp, ext=None, target_str_or_list=None, sort_result=True, recursive=False
):
    # ext can be a list of extensions or a single extension
    # (e.g. ['.jpg', '.png'] or '.jpg')

    fps = get_file_paths_in_dir(
        idp,
        ext=ext,
        target_str_or_list=target_str_or_list,
        sort_result=sort_result,
        recursive=recursive,
    )

    for fp in fps:
        assert os.path.isfile(fp)
        os.remove(fp)


def natural_key(some_string):
    # See http://www.codinghorror.com/blog/archives/001018.html
    return [
        int(s) if s.isdigit() else s for s in re.split(r"(\d+)", some_string)
    ]


def check_ext(ext):
    # Check if extension is valid (contains a leading dot)
    if isinstance(ext, list):
        for ele in ext:
            assert ele[0] == ".", "Invalid extension, leading dot missing"
    else:
        assert ext[0] == ".", "Invalid extension, leading dot missing"


def get_file_paths_in_dir(
    idp,
    ext=None,
    target_str_or_list=None,
    ignore_str_or_list=None,
    base_name_only=False,
    without_ext=False,
    sort_result=True,
    natural_sorting=False,
    recursive=False,
):
    # ext can be a list of extensions or a single extension
    # (e.g. ['.jpg', '.png'] or '.jpg')

    if recursive:
        ifp_s = []
        for root, dirs, files in os.walk(idp):
            ifp_s += [os.path.join(root, ele) for ele in files]
    else:
        ifp_s = [
            os.path.join(idp, ele)
            for ele in os.listdir(idp)
            if os.path.isfile(os.path.join(idp, ele))
        ]

    if ext is not None:
        if isinstance(ext, list):
            ext = [ele.lower() for ele in ext]
            check_ext(ext)
            ifp_s = [
                ifp for ifp in ifp_s if os.path.splitext(ifp)[1].lower() in ext
            ]
        else:
            ext = ext.lower()
            check_ext(ext)
            ifp_s = [
                ifp for ifp in ifp_s if os.path.splitext(ifp)[1].lower() == ext
            ]

    if target_str_or_list is not None and len(target_str_or_list) > 0:
        if type(target_str_or_list) == str:
            target_str_or_list = [target_str_or_list]
        ifp_s_temp = []
        for target_str in target_str_or_list:
            ifp_s_temp += [
                ifp for ifp in ifp_s if target_str in os.path.basename(ifp)
            ]
        ifp_s = ifp_s_temp

    if ignore_str_or_list is not None:
        if type(ignore_str_or_list) == str:
            ignore_str_or_list = [ignore_str_or_list]
        ifp_s_temp = []
        for ignore_str in ignore_str_or_list:
            ifp_s_temp += [
                ifp for ifp in ifp_s if ignore_str not in os.path.basename(ifp)
            ]
        ifp_s = ifp_s_temp

    if base_name_only:
        ifp_s = [os.path.basename(ifp) for ifp in ifp_s]

    if without_ext:
        ifp_s = [os.path.splitext(ifp)[0] for ifp in ifp_s]

    if sort_result:
        if natural_sorting:
            ifp_s = sorted(ifp_s, key=natural_key)
        else:
            ifp_s = sorted(ifp_s)

    return ifp_s


def get_image_file_paths_in_dir(
    idp,
    base_name_only=False,
    without_ext=False,
    sort_result=True,
    recursive=True,
    target_str_or_list=None,
):
    return get_file_paths_in_dir(
        idp,
        ext=[".jpg", ".png"],
        target_str_or_list=target_str_or_list,
        base_name_only=base_name_only,
        without_ext=without_ext,
        sort_result=sort_result,
        recursive=recursive,
    )


def get_corresponding_files_in_directories(
    idp_1, idp_2, ext_1=None, suffix_2="", get_correspondence_callback=None
):

    if get_correspondence_callback is None:

        def get_correspondence_callback(fn_1):
            return fn_1 + suffix_2

    potential_fn_1_list = get_file_paths_in_dir(
        idp_1, ext=ext_1, base_name_only=True
    )
    fp_1_list = []
    fp_2_list = []
    for fn_1 in potential_fn_1_list:
        fp_2 = os.path.join(idp_2, get_correspondence_callback(fn_1))
        if os.path.isfile(fp_2):
            fp_1_list.append(os.path.join(idp_1, fn_1))
            fp_2_list.append(fp_2)
    return fp_1_list, fp_2_list


def get_subdirs(idp, base_name_only=False, recursive=False):

    if recursive:
        sub_dps = []
        if base_name_only:
            for root, dirs, files in os.walk(idp):
                sub_dps += [name for name in dirs]
        else:
            for root, dirs, files in os.walk(idp):
                sub_dps += [os.path.join(root, sub_dn) for sub_dn in dirs]
    else:
        sub_dns = [
            name
            for name in os.listdir(idp)
            if os.path.isdir(os.path.join(idp, name))
        ]
        if base_name_only:
            sub_dps = sub_dns
        else:
            sub_dps = [os.path.join(idp, sub_dn) for sub_dn in sub_dns]

    return sub_dps


def get_stem(ifp, base_name_only=True):
    if base_name_only:
        ifp = os.path.basename(ifp)
    return os.path.splitext(ifp)[0]


def get_basename(ifp):
    return os.path.basename(ifp)


def mkdir_safely(odp):
    if not os.path.isdir(odp):
        os.mkdir(odp)


def makedirs_safely(odp):
    if not os.path.isdir(odp):
        os.makedirs(odp)


def ensure_trailing_slash(some_path):
    return os.path.join(some_path, "")


def get_first_valid_path(list_of_paths):
    first_valid_path = None
    for path in list_of_paths:
        if first_valid_path is None and (
            os.path.isdir(path) or os.path.isfile(path)
        ):
            first_valid_path = path
    return first_valid_path


def get_folders_matching_scheme(path_to_image_folders, pattern):
    target_folder_paths = []
    for root, dirs, files in os.walk(path_to_image_folders):

        match_result = pattern.match(os.path.basename(root))

        if match_result:  # basename matched the pattern
            target_folder_paths.append(root)

    return target_folder_paths


def is_subdir(possible_parent_dir, possible_sub_dir):
    possible_parent_dir = os.path.realpath(possible_parent_dir)
    possible_sub_dir = os.path.realpath(possible_sub_dir)

    return possible_sub_dir.startswith(possible_parent_dir + os.sep)


def exist_files(file_list):
    return all(map(os.path.isfile, file_list))


def are_dirs_equal(idp_1, idp_2):
    fp_1_list = get_file_paths_in_dir(idp_1, base_name_only=True)
    fp_2_list = get_file_paths_in_dir(idp_2, base_name_only=True)

    return fp_1_list == fp_2_list
