import pandas as pd
import numpy as np 
import pathlib
import constants
import logging
FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
#logging.disable(logging.CRITICAL)



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


def ucl_split_detection(mode):

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

if __name__=="__main__":
    ucl_split_detection('x')
    ucl_split_detection('y')