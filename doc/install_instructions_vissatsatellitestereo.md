# Installation Instructions for VisSatSatelliteStereo
 
- Install GDAL
  - Option 1: (Recommended)
    - ```conda install gdal libgdal```
      - Activate (or re-activate) your conda environment and make sure gdal environment variables are correctly configured
        - ```echo $PROJ_LIB```
      - RESTART Pycharm to parse the current environment variables!
    - Tested versions: GDAL 3.3.2 with ```Python 3.8```
  - Option 2:
    - Follow the original GDAL install instructions [here](https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html)
    - Tested versions: GDAL 2.4.2 with ```Python 3.6```, released 2019/06/28


- Install [VisSatSatelliteStereo](https://github.com/Kai-46/VisSatSatelliteStereo)
  - Option 1: Updated VisSatSatelliteStereo (Recommended)
    - ```git clone -b main git@github.com:SBCV/VisSatSatelliteStereo.git```
    - ```pip install -r requirements.txt```
  - Option 2: Original VisSatSatelliteStereo
    - Note: Supports only numpy versions ```< 1.20```
    - Latest tested version of VisSatSatelliteStereo: [commit c6cb1b4](https://github.com/Kai-46/VisSatSatelliteStereo/commit/c6cb1b4ca6bfc6f7210707333db3bbd8931a6265)
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
                - ```numpy-groupies>=0.9.9``` instead of ```numpy-groupies==0.9.9```
                - ```pyproj>=2.4.0``` instead of ```pyproj==2.4.0```
            -->
  - For both options, make sure to ADJUST/REMOVE the ```--SiftExtraction.num_threads 32``` parameter in [colmap_sfm_commands.py](https://github.com/Kai-46/VisSatSatelliteStereo/blob/c6cb1b4ca6bfc6f7210707333db3bbd8931a6265/colmap_sfm_commands.py#L54)
    - See [this issue](https://github.com/Kai-46/VisSatSatelliteStereo/issues/1)
  
