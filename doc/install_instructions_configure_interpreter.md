# Configure Python Interpreter

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
