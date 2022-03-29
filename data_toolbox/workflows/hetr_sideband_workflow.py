import os
from select import select
import numpy as np
import pandas as pd
from data_toolbox.allan_func.allan import overlapping_allan_deviation as oadev
from data_toolbox.allan_func.coefficient_fitting import fit_bias_instability_line
from data_toolbox.allan_func.coefficient_fitting import fit_random_walk_line
from data_toolbox.allan_func.coefficient_fitting import fit_rate_random_walk_line


# Column names to use for the DataFrame
COLUMNS = ["area_x", "freq_x", "linewidth_x", "area_y", "freq_y", "linewidth_y", "residuals"]
SAMPLING_RATE = 1/326.613

def _process(dir, filename):
    
    """
    Load the sideband data from a .dat file. Then, create a DataFrame its contents.

    Args:
        dir (str): Parent directory of the sideband data
        filename (str):  Desired sideband data file. Must be .dat suffix.

    Returns:
        (pandas.DataFrame):  DataFrame from the contents of a sideband data file.
    """
    
    # Check that the filename specifies .dat type
    if not filename.lower().endswith(".dat"):
        raise Exception(f"{filename} must specify the `.dat` extension.")

    # Full path to the specific sideband file
    path2data = os.path.join(dir, filename)

    # Sideband data set as an ndarray
    sideband_array = np.loadtxt(path2data)
    # Convert sideband data into a DataFrame
    return pd.DataFrame(data=sideband_array, columns=COLUMNS)

def _select_column(dir, filename, parameter):
    
    """
    Select a specified column from the sideband DataFrame.

    Raises:
        Exception: When the supplied parameter is not one of the column names.

    Returns:
        numpy.ndarray: Column of the DataFrame as an array.
    """

    # Check that the parameter supplied is a column of the DataFrame
    if parameter not in COLUMNS:
        raise Exception(f"{parameter} not found in {COLUMNS}.")
    
    
    df = _process(dir, filename)
    selected_values = df[parameter]
    return selected_values.to_numpy()

def run_workflow(dir, filename, parameter):
    
    # Measured signal of the time series
    signal = _select_column(dir, filename, parameter)
    
    # Compute the Allan deviation of the signal
    t, s = oadev(signal, SAMPLING_RATE)

    # Estimate the coefficients 
    bias_instability_coeff = fit_bias_instability_line(t, s)
    rate_random_walk_coeff = fit_rate_random_walk_line(t, s)
    random_walk_coeff = fit_random_walk_line(t, s)

    return bias_instability_coeff, rate_random_walk_coeff, random_walk_coeff