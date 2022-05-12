import pandas as pd
import numpy as np 
import data_toolbox.constants as constants
import logging
FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logging.disable(logging.CRITICAL)


### General Helper Functions ###

abbreviate_sideband = lambda sideband: sideband.lower().strip()[0:3]

def load_raw_sideband(sideband):
    """
    Load a `fit_{sideband}_sideband.dat` file into memory as a dataframe.
    
    Assign the column labels according to the ReadMe.txt. 
    Since the ReadMe does not specify the 7th column label, the column
    label is assigned by this function as `error`. 
    
    Args:
        sideband (str, optional):  Heterodyne sideband identifier. 

    Returns:
        (pandas.DataFrame):  A `fit_{sideband}_sideband.dat` file as a dataframe.
    """

    ### Point to the file ###
    # Directory of all raw UCL data
    ucl_fits_path = constants.RAW_DATA_DIRECTORY.joinpath("raw_ucl_fits")
    # Format the filename
    raw_filename_templ = f"fit_{abbreviate_sideband(sideband)}_sideband.dat"
    # Full path to the raw data
    target = ucl_fits_path.joinpath(raw_filename_templ)
    
    ### Format the dataframe ###
    col_names = ["Area_x", "f_x", "linewidth_x", "Area_y", "f_y", "linewidth_y", "error"]
    raw_df = pd.read_csv(target, names=col_names, sep="\t")

    return raw_df

def clean_path(source, mode, sideband=None):

    """
    Create path to a target file in the `clean_data` subdirectory

    Args:
        source (str):  Data source identifier for the clean filename template.
                       Must be either "ucl" or "cst"
        
        mode (str):  Directional mode identifier for the clean filename template.
                     Must be either 'x' or 'y'

        sideband (str, optional):  Sideband identifier for the clean filename template. 
                                   If "positive" or "negative", target is assumed a child of `heterodyne/`
                                   If None, target is assumed to be a child of `split_detection/`
                                   Defaults to None.
    
    Returns:
        (pathlib.ConcretePath):  Object representing path to the target using the OS flavor of path formatting.
    """


    # Assume the filepath is to file in the heterodyne subdirectory
    subdirectory = "heterodyne"

    # A heterodyne sideband is not provided
    # Filepath must be to file in the split detection subdirectory
    if sideband is None:
        # Split detection files always have "none" as their sideband id
        sideband = "none"
        subdirectory = "split_detection"

    # Format the filename
    filename = f"{source}_{mode}_{sideband}.CSV"

    # Path to the desired file
    filepath = constants.CLEAN_DATA_DIRECTORY.joinpath(subdirectory, filename)

    return filepath

def ready_all_ucl():
    
    """
    Convenience function to clean the data from raw UCL fits. 

    Preproccess raw split detection data for each directional mode.
    Preproccess raw heterodyne data for each directional mode and sideband.
    Processed files should be populated under `experiment_data/clean_data/...`
    """

    preprocess_ucl_split_detection('x')
    preprocess_ucl_heterodyne('x', "positive")
    preprocess_ucl_heterodyne('x', "negative")
    preprocess_ucl_split_detection('y')
    preprocess_ucl_heterodyne('y', "positive")
    preprocess_ucl_heterodyne('y', "negative")

    return 

### Data Source Specific Preproccessing Functions ### 
def preprocess_ucl_split_detection(mode):

    """
    Preprocess raw split detection data into a CSV for the specified mode.

    Args:
        mode (str):  Directional mode identifier for the clean filename template.
                     Must be either 'x' or 'y'
    """

    # Directory of all raw UCL data
    ucl_fits_path = constants.RAW_DATA_DIRECTORY.joinpath("raw_ucl_fits")
    

    ### Load time series data for each column into memory ###
    area_under_curve = np.loadtxt(ucl_fits_path.joinpath(f"area{mode}.dat"))
    logging.debug(f"AREA: {area_under_curve}")

    mechanical_frequency = np.loadtxt(ucl_fits_path.joinpath(f"f{mode}.dat"))
    logging.debug(mechanical_frequency)

    # Linewidth data was not fit by UCL. Placeholder signal is used instead.
    # Placeholder has the same shape as area under curve Series.
    aoc_shape = area_under_curve.shape
    linewidth = np.full(shape=aoc_shape, fill_value=-1*np.inf)
    logging.debug(linewidth)
    
    time_step = np.arange(0, len(area_under_curve)) * constants.SPLIT_DETECTION_SAMLPING_STEP_SIZE
    logging.debug(time_step)


    # Read in the clean file as a data frame
    target = clean_path(source="ucl", mode=mode, sideband=None)
    logging.debug(target)
    logging.debug(type(target))

    df = pd.read_csv(target)
    
    # Populate the columns 
    df["area_under_curve"] = area_under_curve
    df["mechanical_frequency"] = mechanical_frequency
    df["linewidth"] = linewidth
    df["time_step"] = time_step

    # Write the populated data frame to the CSV
    df.to_csv(target, index_label="index")

    return 

def preprocess_ucl_heterodyne(mode, sideband):

    ### Locate raw data file ###
    # Load the corresponding heterodyne fit into memory as a dataframe
    df = load_raw_sideband(sideband=sideband)
    # Filter the columns by the directional mode
    matched_df = df.filter(regex=f"\w+{mode}")

    ### Rename the matched column names to the standard set of names ###
    current_names = list(matched_df.columns)
    standard_names = ["area_under_curve" ,"mechanical_frequency" ,"linewidth"]
    name_map = {curr:std for curr,std in list(zip(current_names, standard_names))}
    logging.debug(name_map)
    matched_df = matched_df.rename(columns=name_map)
    logging.debug(f"Matched names: {matched_df.columns}")

    # Create data for time step column
    time_step = np.arange(0, len(matched_df)) * constants.SPLIT_DETECTION_SAMLPING_STEP_SIZE
    # Insert the time step column into the matching dataframe
    matched_df.insert(0, "time_step", time_step)

    ### Write dataframe to file ###
    target = clean_path(source="ucl", mode=mode, sideband=sideband)
    logging.debug(f"Target file {target}")
    matched_df.to_csv(target, index_label="index")
    
    return 

def preprocess_cst_split_detection(mode):
    pass
    return 

def preprocess_cst_heterodyne(mode, sideband):
    pass
    return 