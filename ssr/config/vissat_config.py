import os
import json


def create_vissat_config(
    vissat_config_ofp,
    dataset_dp,
    workspace_dp,
    # Bounding Box Options
    zone_number,
    hemisphere,
    ul_easting,
    ul_northing,
    width,
    height,
    # Altitude
    alt_min,
    alt_max,
    # Steps to Run Options
    clean_data=True,
    crop_image=True,
    derive_approx=True,
    choose_subset=True,
    colmap_sfm_perspective=True,
    inspect_sfm_perspective=True,
    reparam_depth=True,
    colmap_mvs=True,
    aggregate_2p5d=True,
    aggregate_3d=True,
):
    """This function creates a config file used by the VisSat pipeline.

    The created json file contains something like:
    {
      "dataset_dir": "/path/tospacenet-dataset/Hosted-Datasets/MVS_dataset/WV3/PAN",
      "work_dir": "/path/to/IARPA_MVS3DM_reconstruction",
      "bounding_box": {
        "zone_number": 21,
        "hemisphere": "S",
        "ul_easting": 354035.0,
        "ul_northing": 6182717.0,
        "width": 745.0,
        "height": 682.0
      },
      "steps_to_run": {
        "clean_data": true,
        "crop_image": true,
        "derive_approx": true,
        "choose_subset": true,
        "colmap_sfm_perspective": true,
        "inspect_sfm_perspective": true,
        "reparam_depth": true,
        "colmap_mvs": true,
        "aggregate_2p5d": true,
        "aggregate_3d": true
      },
      "alt_min": -20.0,
      "alt_max": 100.0
    }
    """

    bounding_box = {
        "zone_number": zone_number,
        "hemisphere": hemisphere,
        "ul_easting": ul_easting,
        "ul_northing": ul_northing,
        "width": width,
        "height": height,
    }

    steps_to_run = {
        "clean_data": clean_data,
        "crop_image": crop_image,
        "derive_approx": derive_approx,
        "choose_subset": choose_subset,
        "colmap_sfm_perspective": colmap_sfm_perspective,
        "inspect_sfm_perspective": inspect_sfm_perspective,
        "reparam_depth": reparam_depth,
        "colmap_mvs": colmap_mvs,
        "aggregate_2p5d": aggregate_2p5d,
        "aggregate_3d": aggregate_3d,
    }

    vissat_config = {
        "dataset_dir": dataset_dp,
        "work_dir": workspace_dp,
        "bounding_box": bounding_box,
        "steps_to_run": steps_to_run,
        "alt_min": alt_min,
        "alt_max": alt_max,
    }

    with open(vissat_config_ofp, "w") as fp:
        json.dump(vissat_config, fp, indent=2)


def create_vissat_config_from_ssr_config(
    vissat_config_ofp,
    dataset_dp,
    workspace_dp,
    ssr_config,
    clean_data,
    crop_image,
    derive_approx,
    choose_subset,
    colmap_sfm_perspective,
    inspect_sfm_perspective,
    reparam_depth,
    colmap_mvs,
    aggregate_2p5d,
    aggregate_3d,
):
    """ The created config uses the PAN images"""

    create_vissat_config(
        vissat_config_ofp,
        dataset_dp=dataset_dp,
        workspace_dp=workspace_dp,
        # Bounding Box Options
        zone_number=ssr_config.zone_number,
        hemisphere=ssr_config.hemisphere,
        ul_easting=ssr_config.ul_easting,
        ul_northing=ssr_config.ul_northing,
        width=ssr_config.width,
        height=ssr_config.height,
        # Altitude
        alt_min=ssr_config.alt_min,
        alt_max=ssr_config.alt_max,
        # Steps to Run Options
        clean_data=clean_data,
        crop_image=crop_image,
        derive_approx=derive_approx,
        choose_subset=choose_subset,
        colmap_sfm_perspective=colmap_sfm_perspective,
        inspect_sfm_perspective=inspect_sfm_perspective,
        reparam_depth=reparam_depth,
        colmap_mvs=colmap_mvs,
        aggregate_2p5d=aggregate_2p5d,
        aggregate_3d=aggregate_3d,
    )


def create_vissat_extraction_config(
    vissat_config_ofp, dataset_dp, workspace_dp, ssr_config
):
    create_vissat_config_from_ssr_config(
        vissat_config_ofp=vissat_config_ofp,
        dataset_dp=dataset_dp,
        workspace_dp=workspace_dp,
        ssr_config=ssr_config,
        clean_data=True,
        crop_image=True,
        derive_approx=False,
        choose_subset=False,
        colmap_sfm_perspective=False,
        inspect_sfm_perspective=False,
        reparam_depth=False,
        colmap_mvs=False,
        aggregate_2p5d=False,
        aggregate_3d=False,
    )


if __name__ == "__main__":
    vissat_config_ofp = "/path/to/vissat_config.json"
    dataset_dp = "/path/to//msi"
    workspace_dp = "/path/to/workspace"

    create_vissat_config(
        vissat_config_ofp,
        dataset_dp,
        workspace_dp,
        # Bounding Box Options
        zone_number=21,
        hemisphere="S",
        ul_easting=354035.0,
        ul_northing=6182717.0,
        width=745.0,
        height=682.0,
        # Altitude
        alt_min=-20.0,
        alt_max=100.0,
        # Steps to Run Options
        clean_data=True,
        crop_image=True,
        derive_approx=True,
        choose_subset=True,
        colmap_sfm_perspective=True,
        inspect_sfm_perspective=True,
        reparam_depth=True,
        colmap_mvs=True,
        aggregate_2p5d=True,
        aggregate_3d=True,
    )
