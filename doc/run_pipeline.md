# Run the SSR Pipeline

- The starting point of the SSR pipeline is ```ssr/run_pipeline.py```
- The first time ```ssr/run_pipeline.py``` is executed, it will create a configuration at ```ssr/configs/pipeline.toml``` using the template located at ```ssr/configs/pipeline_template.toml```

- Adjust the paths in the config file ```ssr/configs/pipeline.toml```
    - For the executables (```fp = file path```, ```dp = directory path```)
        - ```colmap_vissat_exe_fp```
        - ```mve_apps_dp```
        - ```texrecon_apps_dp```
        - ```gdmr_bin_dp```
        - ```openmvs_bin_dp```
        - ```colmap_exe_dp```
        - ```meshlab_server_fp```
        
    - For the reconstruction results (i.e. workspace directories)
        - ```workspace_vissat_dp```
        - ```workspace_ssr_dp```
        - ```meshlab_temp_dp```

    - For the input data uncomment the relevant block in the config (depending on the input dataset)
      - Option 1: [IARPA MVS3DM dataset](https://spacenet.ai/iarpa-multi-view-stereo-3d-mapping/) 
        - ```dataset_adapter = "ssr.input_adapters.adapter_MVS3DM"```
        - ```satellite_image_pan_dp=/path/to/spacenet-dataset/Hosted-Datasets/MVS_dataset/WV3/PAN```
        - ```satellite_image_msi_dp=/path/to/spacenet-dataset/Hosted-Datasets/MVS_dataset/WV3/MSI```
      - Option 2: [Data Fusion Contest 2019 (dfc2019) Track 3 dataset](https://ieee-dataport.org/open-access/data-fusion-contest-2019-dfc2019)
        - ```dataset_adapter = "ssr.input_adapters.adapter_DFC2019"```
        - ```satellite_image_rgb_tif_dp = "path/to/input/tif/files"```
          - Note: the [dfc2019 Track 3 dataset](https://ieee-dataport.org/open-access/data-fusion-contest-2019-dfc2019)
            contains data for multiple location sites. The SSR pipeline expects ```satellite_image_rgb_tif_dp``` to point to a directory containing
            a subset of the data belonging to the same location (for example ```JAX_004_*_RGB.tif```)
          - If the relevant ```.txt``` file from ```Track 3 / Training data / Reference Train-Track3-Truth.zip``` (for example ```JAX_004_DSM.txt``` ) is placed in the same input directory and ```ul_easting, ul_northing, width, height``` are **not** set, they will be calculated based on the ```.txt``` file.

- Adjust the list of ```meshing_backends``` according to the installed MVS / Surface reconstruction libraries
    - For example, comment ```Openmvs``` in ```meshing_backends```, if it is not available 
- Run ```ssr/run_pipeline.py```
- The final output of the pipeline based on the meshing backends chosen can be found in ```workspace_ssr_dp/surface/surface/mve/```
