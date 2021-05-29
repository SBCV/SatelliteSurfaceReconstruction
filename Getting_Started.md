# Installation Instructions for Ubuntu 18.04

- Install Python 3.6, 3.7 or 3.8
    - We have tested the pipeline with Python 3.8
    - The library versions in ```SatelliteSurfaceReconstruction/requirements.txt``` might differ for Python 3.6 and 3.7

- Install [VisSat](https://openaccess.thecvf.com/content_ICCVW_2019/html/3DRW/Zhang_Leveraging_Vision_Reconstruction_Pipelines_for_Satellite_Imagery_ICCVW_2019_paper.html)
    - Follow the [install instructions of ColmapForVisSat](https://github.com/Kai-46/ColmapForVisSat)
        - Make sure you have installed a compatible cuda version (e.g. ```Cuda 10.0```)
            - ```Cuda 10.0``` can be installed following [this link](https://developer.nvidia.com/cuda-10.0-download-archive?target_os=Linux&target_arch=x86_64).
        - To avoid that incorrect libraries are detetected by CMake, consider to disable the active anaconda/miniconda environment with `conda deactivate`
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
        - Make sure to ADJUST the ```--SiftExtraction.num_threads 32``` parameter
            - See [this issue](https://github.com/Kai-46/VisSatSatelliteStereo/issues/1)
   
- Install at least one of the following MVS & surface reconstruction libraries
    - ColmapForVisSat / Colmap
        - See installation instructions above
    - [MVE](https://www.gcc.tu-darmstadt.de/media/gcc/papers/Fuhrmann-2014-MVE.pdf) with [FSSR](https://www.gcc.tu-darmstadt.de/media/gcc/papers/Fuhrmann-2014-FSS.pdf)
        - Follow the [installation instructions of MVE](https://github.com/simonfuhrmann/mve)
        - Note: FSSR is part of the MVE library 
    - [GDMR](https://lmb.informatik.uni-freiburg.de/Publications/2017/UB17/ummenhofer2017Global.pdf) (requires MVE)
        - Follow the [installation instructions of MVE](https://github.com/simonfuhrmann/mve)
        - Follow the [installation instructions of GDMR](https://lmb.informatik.uni-freiburg.de/people/ummenhof/multiscalefusion/) 
    - OpenMVS
        - Follow the [installation instructions of OpenMVS](https://github.com/cdcseacave/openMVS)


- Install [MVS-Texturing](https://www.gcc.tu-darmstadt.de/media/gcc/papers/Waechter-2014-LTB.pdf) (requires MVE)
    - Follow the [installation instructions of MVS-Texturing](https://github.com/nmoehrle/mvs-texturing)
   
- Install [Meshlab](https://github.com/cnr-isti-vclab/meshlab) 
    - For a list of releases see [here](https://github.com/cnr-isti-vclab/meshlab/releases) 

- Make [VisSatSatelliteStereo](https://github.com/Kai-46/VisSatSatelliteStereo) and ```SatelliteSurfaceReconstruction``` available to your python interpreter
    - Option 1: Add `VisSatSatelliteStereo` and `SatelliteSurfaceReconstruction` to the python path
        - Add `ssr` (in the `SatelliteSurfaceReconstruction` directory)
            - export PYTHONPATH="${PYTHONPATH}:/path/to/SatelliteSurfaceReconstruction"
        - Add `lib` etc. (in the `VisSatSatelliteStereo` directory)
            - export PYTHONPATH="${PYTHONPATH}:/path/to/VisSatSatelliteStereo"
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

- Download the [IARPA MVS3DM dataset](https://spacenet.ai/iarpa-multi-view-stereo-3d-mapping/) 
    - Note: The dataset location referenced at [IARPA MVS3DM dataset](https://spacenet.ai/iarpa-multi-view-stereo-3d-mapping/) is incorrect
    - Instead you can download the dataset (using [amazon web services](https://aws.amazon.com)) with
        - ```aws s3 cp s3://spacenet-dataset/Hosted-Datasets/MVS_dataset/ /local/path/to/dataset/```
    - If you want to inspect the data before downloading you might want to use 
        - ```aws s3 ls s3://spacenet-dataset/Hosted-Datasets/MVS_dataset/```


# Run the SSR Pipeline

- The starting point of the SSR pipeline is ```ssr/run_pipeline.py```
- The first time ```ssr/run_pipeline.py``` is executed, it will create a configuration at ```ssr/configs/pipeline.cfg``` using the template located at ```ssr/configs/pipeline_template.cfg```

- Adjust the paths in the config file ```ssr/configs/pipeline.cfg```
    - For the executables (```fp = file path```, ```dp = directory path```)
        - ```colmap_vissat_exe_fp```
        - ```mve_apps_dp```
        - ```texrecon_apps_dp```
        - ```gdmr_bin_dp```
        - ```openmvs_bin_dp```
        - ```colmap_exe_dp```
        - ```meshlab_server_fp```

    - For the input data
        - ```satellite_image_pan_dp=/path/to/spacenet-dataset/Hosted-Datasets/MVS_dataset/WV3/PAN```
        - ```satellite_image_msi_dp=/path/to/spacenet-dataset/Hosted-Datasets/MVS_dataset/WV3/MSI```
        
    - For the reconstruction results (i.e. workspace directories)
        - ```workspace_vissat_dp```
        - ```workspace_ssr_dp```
        - ```meshlab_temp_dp```

- Adjust the list of ```meshing_backends``` according to the installed MVS / Surface reconstruction libraries
    - For example, uncomment ```Openmvs``` in ```meshing_backends```, if it is not available 
- Run ```ssr/run_pipeline.py```

# Trouble Shooting / Debugging
- If you receive ```ModuleNotFoundError: No module named 'lib'``` at ```from lib.rpc_model import RPCModel```, then the [VisSatSatelliteStereo library](https://github.com/Kai-46/VisSatSatelliteStereo) is not available in your python environment.
- If the pipeline does not successfully terminate, use the values in ```pipeline.cfg``` to run only specific parts of the pipeline
    - For example, to run only VisSat use
        - ```reconstruct_sfm_mvs = 1```
        - ```extract_pan = 0```
        - ```extract_msi = 0```
        - ```pan_sharpening = 0```
        - ```depth_map_recovery = 0```
        - ```skew_correction = 0```
        - ```reconstruct_mesh = 0```
        - ```texture_mesh = 0```
