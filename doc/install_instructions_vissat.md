# Installation Instructions for VisSat

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
    
 