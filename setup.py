import os

# Full path to the location of this file
PREFIX = os.getcwd()
# Top level directory for data
EXPERIMENT_TOP = os.path.join(PREFIX, "experiment_data/")
# Subdirectory for raw split band data
SPLIT_DETECTION_RAW = os.path.join(EXPERIMENT_TOP, "split_detection/")
# Subdirectory for raw heterodyne data
HETERODYNE_RAW = os.path.join(EXPERIMENT_TOP, "heterodyne/")
# Subdirectory for time series created by UCL experimenters
UCL_TIME_SERIES = os.path.join(EXPERIMENT_TOP, "ucl_time_series/")

# Callable dictionary of paths through the experiment data directory
PATHS = {
    "ucl":UCL_TIME_SERIES,
    "hetr":HETERODYNE_RAW,
    "split":SPLIT_DETECTION_RAW
}

def build_file_tree():
    """
    Create a directory where experiment data will be stored.
    If the directory already exists, do not create anything.
    """
    try:
        print("Building file tree...")
        
        # Ensure starting at PREFIX
        os.chdir(PREFIX)

        # Create the file tree with the top level at the same level as this file
        os.mkdir(EXPERIMENT_TOP)
        # Move into the top level of the new file tree
        os.chdir(EXPERIMENT_TOP)
        # Create the subdirectories
        os.mkdir(SPLIT_DETECTION_RAW)
        os.mkdir(HETERODYNE_RAW)
        os.mkdir(UCL_TIME_SERIES)
        
        print(f"Complete! Extract data files accordingly within `{EXPERIMENT_TOP}`")

    except FileExistsError:
        print(f"File tree is already set up. Extract data files accordingly within `{EXPERIMENT_TOP}`")

    return 
