# Installation Instructions for Ubuntu 18.04

- Install Python 3.6, 3.7 or 3.8
    - We have tested the pipeline with Python 3.8
    - The library versions in ```SatelliteSurfaceReconstruction/requirements.txt``` might differ for Python 3.6 and 3.7

- Install [VisSat](https://openaccess.thecvf.com/content_ICCVW_2019/html/3DRW/Zhang_Leveraging_Vision_Reconstruction_Pipelines_for_Satellite_Imagery_ICCVW_2019_paper.html)
    - Install [ColmapForVisSat](https://github.com/Kai-46/ColmapForVisSat) or [ColmapForVisSatPatched](https://github.com/SBCV/ColmapForVisSatPatched)
        - Option 1: ColmapForVisSatPatched (RECOMMENDED)
            - Follow the [install instructions](https://github.com/SBCV/ColmapForVisSatPatched#build-patched-colmap-repository)
                - sudo apt-get install libmetis-dev
                - To avoid that incorrect libraries are detected by CMake, consider to disable the active anaconda/miniconda environment with `conda deactivate`
                - Follow the official install instructions of [Colmap (for linux)](https://colmap.github.io/install.html#linux)
        - Option 2: ColmapForVisSat 
            - Follow the [install instructions](https://github.com/Kai-46/ColmapForVisSat)
                - Make sure you have installed a compatible cuda version (e.g. ```Cuda 10.0```)
                    - ```Cuda 10.0``` can be installed following [this link](https://developer.nvidia.com/cuda-10.0-download-archive?target_os=Linux&target_arch=x86_64).
                - To avoid that incorrect libraries are detected by CMake, consider to disable the active anaconda/miniconda environment with `conda deactivate`
                - Clone the repository
                    - ```git clone https://github.com/Kai-46/ColmapForVisSat.git```
                - Execute ``ubuntu1804_install_dependencies.sh``
                - Execute ``ubuntu1804_install_colmap.sh``
    
    - Follow the [install instructions of VisSatSatelliteStereo](https://github.com/Kai-46/VisSatSatelliteStereo)
        - Install GDAL
            - See the [installation instructions of gdal](https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html)
        - Clone the repository
            - ```git clone https://github.com/Kai-46/VisSatSatelliteStereo```
            - ```pip install -r requirements.txt```
                - For Python 3.8 use our ```SatelliteSurfaceReconstruction/requirements.txt``` instead of ```VisSatSatelliteStereo/requirements.txt```
                <!--
                - The library versions have been adjusted for Python 3.8 including: 
                    - ```lxml>=4.3.0``` instead of ```lxml==4.3.0```
                    - ```matplotlib==3.2.1``` instead of ```matplotlib==3.0.0```
                    - ```numba>=0.41``` instead of ```numba==0.41.0```
                    - ```numpy>=1.17``` instead of ```numpy==1.15.4```
                    - ```scipy>=1.1``` instead of ```scipy==1.1.0```
                    - ```opencv-python>=4.0``` instead of ```opencv-python==4.0.0.21```
                    - ```open3d-python==0.6.0.0``` deleted
                    - ```numpy-groupies>=0.9.9``` instead of ```numpy-groupies>=0.9.9```
                    - ```pyproj>=2.4.0``` instead of ```pyproj==2.4.0```
                -->
        - Make sure to ADJUST the ```--SiftExtraction.num_threads 32``` parameter in [colmap_sfm_commands.py](https://github.com/Kai-46/VisSatSatelliteStereo/blob/c6cb1b4ca6bfc6f7210707333db3bbd8931a6265/colmap_sfm_commands.py#L54)
            - See [this issue](https://github.com/Kai-46/VisSatSatelliteStereo/issues/1)
   
- Install at least one of the following MVS & surface reconstruction libraries
    - ColmapForVisSat / Colmap
        - See installation instructions above
    - [MVE](http://www.simonfuhrmann.de/papers/gch2014-mve.pdf) with [FSSR](http://www.simonfuhrmann.de/papers/sg2014-fssr.pdf)
        - Follow the [installation instructions of MVE](https://github.com/simonfuhrmann/mve)
        - Note: FSSR is part of the MVE library 
    - [GDMR](https://lmb.informatik.uni-freiburg.de/Publications/2017/UB17/ummenhofer2017Global.pdf) (requires MVE)
        - Follow the [installation instructions of MVE](https://github.com/simonfuhrmann/mve)
        - Follow the [installation instructions of GDMR](https://lmb.informatik.uni-freiburg.de/people/ummenhof/multiscalefusion/) 
    - OpenMVS
        - Follow the [installation instructions of OpenMVS](https://github.com/cdcseacave/openMVS)


- Install [MVS-Texturing](https://github.com/nmoehrle/mvs-texturing) (requires MVE)
    - Follow the [installation instructions of MVS-Texturing](https://github.com/nmoehrle/mvs-texturing)
   
- Install [Meshlab](https://github.com/cnr-isti-vclab/meshlab) 
    - Make sure to install [Meshlab-2020.09](https://github.com/cnr-isti-vclab/meshlab/releases/tag/Meshlab-2020.09) or older
    - Newer versions do not include the required meshlabserver anymore
    - For a list of releases see [here](https://github.com/cnr-isti-vclab/meshlab/releases) 

- Make [VisSatSatelliteStereo](https://github.com/Kai-46/VisSatSatelliteStereo) and ```SatelliteSurfaceReconstruction``` available to your python interpreter
    - Option 1: Add `VisSatSatelliteStereo` and `SatelliteSurfaceReconstruction` to the python path
        - Add `ssr` (in the `SatelliteSurfaceReconstruction` directory)
            - `export PYTHONPATH="${PYTHONPATH}:/path/to/SatelliteSurfaceReconstruction"`
        - Add `lib` etc. (in the `VisSatSatelliteStereo` directory)
            - `export PYTHONPATH="${PYTHONPATH}:/path/to/VisSatSatelliteStereo"`
        - This allows to run your pipeline (later) with
            - `cd /path/to/SatelliteSurfaceReconstruction/ssr`
            - `python run_pipeline.py` (see the section `Run the SSR Pipeline` below)
        
    - Option 2: Use and IDE like Pycharm to manage the project dependencies
        - For example in ```Pycharm```
            - `File` / `Open...` / Select ```SatelliteSurfaceReconstruction```
            - `File` / `Open...` / Select ```VisSatSatelliteStereo``` and attach it to the current ```SatelliteSurfaceReconstruction``` project
            - Go to ```File / Settings / Project: SatelliteSurfaceReconstruction / Project Dependencies ```
                - Select ```SatelliteSurfaceReconstruction```
                - Make sure that ```VisSatSatelliteStereo``` is selected


# Download Satellite Images

The pipeline can use either the [IARPA MVS3DM dataset](https://spacenet.ai/iarpa-multi-view-stereo-3d-mapping/) or [Data Fusion Contest 2019 (dfc2019) Track 3](https://ieee-dataport.org/open-access/data-fusion-contest-2019-dfc2019)
dataset

- Download either the [IARPA MVS3DM dataset](https://spacenet.ai/iarpa-multi-view-stereo-3d-mapping/) 
    - Note: The dataset location referenced at [IARPA MVS3DM dataset](https://spacenet.ai/iarpa-multi-view-stereo-3d-mapping/) is incorrect
    - Instead you can download the dataset (using [amazon web services](https://aws.amazon.com)) with
        - ```aws s3 cp s3://spacenet-dataset/Hosted-Datasets/MVS_dataset/ /local/path/to/dataset/ --recursive```
    - If you want to inspect the data before downloading you might want to use 
        - ```aws s3 ls s3://spacenet-dataset/Hosted-Datasets/MVS_dataset/```

- **OR** Download the [Data Fusion Contest 2019 (dfc2019) Track 3](https://ieee-dataport.org/open-access/data-fusion-contest-2019-dfc2019)
  - Note: The relevant data is contained inside 
    - ```Track 3 / Training data / RGB images 1/2 Train-Track3-RGB-1.zip```
    - ```Track 3 / Training data / RGB images 2/2 Train-Track3-RGB-1.zip```
    - ```Track 3 / Training data / Reference Train-Track3-Truth.zip```

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

    - For the input data based on the dataset used as input uncomment the relevant block in the config
      - When using the [IARPA MVS3DM dataset](https://spacenet.ai/iarpa-multi-view-stereo-3d-mapping/) 
        - ```dataset_adapter = "ssr.input_adapters.adapter_MVS3DM"```
        - ```satellite_image_pan_dp=/path/to/spacenet-dataset/Hosted-Datasets/MVS_dataset/WV3/PAN```
        - ```satellite_image_msi_dp=/path/to/spacenet-dataset/Hosted-Datasets/MVS_dataset/WV3/MSI```
      - When using the [Data Fusion Contest 2019 (dfc2019) Track 3 dataset](https://ieee-dataport.org/open-access/data-fusion-contest-2019-dfc2019)
        - ```dataset_adapter = "ssr.input_adapters.adapter_DFC2019"```
        - ```satellite_image_rgb_tif_dp = "path/to/input/tif/files"```
          - Note: the [dfc2019 Track 3 dataset](https://ieee-dataport.org/open-access/data-fusion-contest-2019-dfc2019)
            contains data for multiple location sites. The SSR pipeline expects ```satellite_image_rgb_tif_dp``` to point to a directory containing
            a subset of the data belonging to the same location (for example ```JAX_004_*_RGB.tif```)
          - If the relevant .txt from ```Track 3 / Training data / Reference Train-Track3-Truth.zip``` (for example ```JAX_004_DSM.txt``` ) is placed in the same input directory
            and ```ul_easting, ul_northing, width, height``` are **not** set, they will be calculated based on the .txt

- Adjust the list of ```meshing_backends``` according to the installed MVS / Surface reconstruction libraries
    - For example, comment ```Openmvs``` in ```meshing_backends```, if it is not available 
- Run ```ssr/run_pipeline.py```
- The final output of the pipeline based on the meshing backends chosen can be found in ```workspace_ssr_dp/surface/surface/mve/```

# Trouble Shooting / Debugging
- If you receive ```ModuleNotFoundError: No module named 'lib'``` at ```from lib.rpc_model import RPCModel```, then the [VisSatSatelliteStereo library](https://github.com/Kai-46/VisSatSatelliteStereo) is not available in your python environment.
- If the pipeline does not successfully terminate, use the values in ```pipeline.cfg``` to run only specific parts of the pipeline
    - For example, to run only VisSat use
        - ```reconstruct_sfm_mvs = 1```
        - ```extract_pan = 0```
        - ```extract_msi = 0```
        - ```run_input_adapter = 1```
        - ```pan_sharpening = 0```
        - ```depth_map_recovery = 0```
        - ```skew_correction = 0```
        - ```reconstruct_mesh = 0```
        - ```texture_mesh = 0```
