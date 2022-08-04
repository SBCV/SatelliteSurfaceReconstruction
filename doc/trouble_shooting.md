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
