import pathlib



### Directory paths ###
PACKAGE_DIRECTORY = pathlib.Path(__file__).parents[1]
EXPERIMENT_DATA_DIRECTORY = PACKAGE_DIRECTORY.joinpath("experiment_data")
RAW_DATA_DIRECTORY = EXPERIMENT_DATA_DIRECTORY.joinpath("raw_data")
CLEAN_DATA_DIRECTORY = EXPERIMENT_DATA_DIRECTORY.joinpath("clean_data")

### Sampling ###
HETERODYNE_SAMPLING_STEP_SIZE = 326.613 # Seconds
SPLIT_DETECTION_SAMLPING_STEP_SIZE = 772.26 # Seconds

### Units ###
SPLIT_DETECTION_UNITS = "m^2/Hz"
HETERODYNE_UNITS = "V^2/Hz"