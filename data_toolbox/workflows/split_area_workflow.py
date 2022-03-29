import os
import numpy as np
import pandas as pd
from data_toolbox.allan_func.allan import overlapping_allan_deviation as oadev
from data_toolbox.allan_func.coefficient_fitting import fit_bias_instability_line
from data_toolbox.allan_func.coefficient_fitting import fit_random_walk_line
from data_toolbox.allan_func.coefficient_fitting import fit_rate_random_walk_line


# Column names to use for the DataFrame
COLUMNS = ["area"]

# Split detection data is sampled every 772.26 seconds
SAMPLING_RATE = 1/772.26


def _process_ucl_area(dir, filename):
    
    """
    Load the area data from a .dat file. Then, create a DataFrame its contents.

    Args:
        dir (str): Parent directory of the area data.
        filename (str):  Desired area data file. Must be .dat suffix.

    Returns:
        (pandas.DataFrame):  DataFrame from the contents of a area data file.
    """
    
    # Check that the filename specifies .dat type
    if not filename.lower().endswith(".dat"):
        raise Exception(f"{filename} must specify the `.dat` extension.")

    # Full path to the specific sideband file
    path2data = os.path.join(dir, filename)

    # Area data set as an ndarray
    area_array = np.loadtxt(path2data)
    # Convert area data into a DataFrame
    return pd.DataFrame(data=area_array, columns=COLUMNS)

def _get_area(dir, filename):
    """
    Create an array of area values.

    Args:
        dir (str): Parent directory of the sideband data.
        filename (str):  Desired area data file. Must be .dat suffix.

    Returns:
        numpy.ndarray: Area values as an array.
    """

    # Create a dataframe from the area data
    df = _process_ucl_area(dir, filename)

    # Since there is only one column in this data set, select it
    area_values = df["area"]

    return area_values.to_numpy()

def run_ucl_workflow(dir, filename):
    
    """
    Specify a column to analyze. Compute the Allan deviation of the selected parameter.
    Estimate the BI, RW, and RRW of the selected parameter.

    Args:
        dir (str): Parent directory of the area data.
        filename (str):  Desired area data file. Must be .dat suffix.

    Returns:
        ([numpy.ndarray, numpy.ndarray, numpy.ndarray]):  A list of the estimated coefficients.
    """
    
    # Measured signal of the time series
    signal = _get_area(dir, filename)
    
    # Compute the Allan deviation of the signal
    t, s = oadev(signal, SAMPLING_RATE)

    # Estimate the coefficients 
    bias_instability_coeff = fit_bias_instability_line(t, s)
    rate_random_walk_coeff = fit_rate_random_walk_line(t, s)
    random_walk_coeff = fit_random_walk_line(t, s)

    return bias_instability_coeff, rate_random_walk_coeff, random_walk_coeff