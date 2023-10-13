# Installation Instructions for Ubuntu 18.04

- Install Python 3.6, 3.7 or 3.8
    - We have tested the pipeline with Python 3.8
    - The library versions in ```SatelliteSurfaceReconstruction/requirements.txt``` might differ for Python 3.6 and 3.7
- Install the freeimage plugin for imageio
  - Activate your conda environment (e.g. ```conda activate <ssr_conda_environment_name>```)
  - Start an interactive python session (i.e. by typing ```python```)
  - Download and install the freeimage plugin
    - ```>>> import imageio``` 
    - ```>>> imageio.plugins.freeimage.download()```
- Install [VisSat](https://openaccess.thecvf.com/content_ICCVW_2019/html/3DRW/Zhang_Leveraging_Vision_Reconstruction_Pipelines_for_Satellite_Imagery_ICCVW_2019_paper.html)
    - Install [ColmapForVisSat](https://github.com/Kai-46/ColmapForVisSat) or [ColmapForVisSatPatched](https://github.com/SBCV/ColmapForVisSatPatched)
        - Option 1: ColmapForVisSatPatched (RECOMMENDED)
            - Follow the [install instructions](https://github.com/SBCV/ColmapForVisSatPatched#build-patched-colmap-repository)
                - sudo apt-get install libmetis-dev (Latest tested version: 5.1.0.dfsg-5)
                - To avoid that incorrect libraries are detected by CMake, consider to disable the active anaconda/miniconda environment with `conda deactivate`
                - Follow the official install instructions of [Colmap (for linux)](https://colmap.github.io/install.html#linux)
                  - Latest tested version: [commit 31df46c](https://github.com/colmap/colmap/commit/31df46c6c82bbdcaddbca180bc220d2eab9a1b5e)
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
        - Latest tested version of VisSatSatelliteStereo: [commit c6cb1b4](https://github.com/Kai-46/VisSatSatelliteStereo/commit/c6cb1b4ca6bfc6f7210707333db3bbd8931a6265)
        - Install GDAL
            - See the [installation instructions of gdal](https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html)
            - Latest tested version: GDAL 2.4.2, released 2019/06/28
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
        - Latest tested version: [commit 354a652](https://github.com/simonfuhrmann/mve/commit/354a652461377939ca136f451ba3271a1c52ee65)
    - [GDMR](https://lmb.informatik.uni-freiburg.de/Publications/2017/UB17/ummenhofer2017Global.pdf) (requires MVE)
        - Follow the [installation instructions of MVE](https://github.com/simonfuhrmann/mve)
        - Follow the [installation instructions of GDMR](https://lmb.informatik.uni-freiburg.de/people/ummenhof/multiscalefusion/) 
        - Latest tested version: 0.2.0
    - OpenMVS
        - Follow the [installation instructions of OpenMVS](https://github.com/cdcseacave/openMVS)
        - Latest tested version: [v2.1.0 ](https://github.com/cdcseacave/openMVS/commit/f62b38d5d02266452bb16dbcf153963001c09f93)


- Install [MVS-Texturing](https://github.com/nmoehrle/mvs-texturing) (requires MVE)
    - Follow the [installation instructions of MVS-Texturing](https://github.com/nmoehrle/mvs-texturing)
    - Latest tested version: [commit 1a8603e](https://github.com/nmoehrle/mvs-texturing/commit/1a8603e7804e679f329885bceeb3bea1d156be02)
   
- Install [Meshlab](https://github.com/cnr-isti-vclab/meshlab) 
    - Make sure to install [Meshlab-2020.09](https://github.com/cnr-isti-vclab/meshlab/releases/tag/Meshlab-2020.09) or older
      - For example download ```MeshLab2020.09-linux.snap``` and execute ```snap install ./MeshLab2020.09-linux.snap --dangerous``` 
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
