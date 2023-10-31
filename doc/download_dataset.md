# Download and Prepare Satellite Images

The pipeline allows to process the [IARPA MVS3DM dataset](https://spacenet.ai/iarpa-multi-view-stereo-3d-mapping/) or the [Data Fusion Contest 2019 (dfc2019) Track 3](https://ieee-dataport.org/open-access/data-fusion-contest-2019-dfc2019) dataset.

- Option 1: Download the [IARPA MVS3DM dataset](https://spacenet.ai/iarpa-multi-view-stereo-3d-mapping/)
    - Note: The dataset location referenced at [IARPA MVS3DM dataset](https://spacenet.ai/iarpa-multi-view-stereo-3d-mapping/) is incorrect
    - Instead you can download the dataset (using [amazon web services](https://aws.amazon.com)) with
        - ```aws s3 cp s3://spacenet-dataset/Hosted-Datasets/MVS_dataset/ /local/path/to/dataset/ --recursive```
    - If you want to inspect the data before downloading you might want to use 
        - ```aws s3 ls s3://spacenet-dataset/Hosted-Datasets/MVS_dataset/```

- Option 2: Download the [Data Fusion Contest 2019 (dfc2019) Track 3](https://ieee-dataport.org/open-access/data-fusion-contest-2019-dfc2019)
  - Note: The relevant data is contained in
    - ```Track 3 / Training data / RGB images 1/2 Train-Track3-RGB-1.zip```
    - ```Track 3 / Training data / RGB images 2/2 Train-Track3-RGB-1.zip```
    - ```Track 3 / Training data / Reference Train-Track3-Truth.zip```
  - Run ```prepare_dataset.prepare_dfc2019_data.py``` which reorganizes the data into single sites 
    - ```
      dataset_track3_prepared
      └───JAX_004
      │   │───JAX_004_006_RGB.tif
      │   │───...
      │   └───JAX_004_DSM.txt
      └───JAX_017
      │   │───JAX_017_001_RGB.tif
      │   │───...
      │   └───JAX_017_DSM.txt
      ```
