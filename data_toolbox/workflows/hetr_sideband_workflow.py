import os
import numpy as np
import pandas as pd
from data_toolbox.allan_func.allan import overlapping_allan_deviation as oadev
from data_toolbox.allan_func.coefficient_fitting import fit_bias_instability_line
from data_toolbox.allan_func.coefficient_fitting import fit_random_walk_line
from data_toolbox.allan_func.coefficient_fitting import fit_rate_random_walk_line


# Sideband fit data contains the first six entries as column names
# The 7th entry is assumed to be an error/residuals column
# (Source:  UCL Data README)
COLUMNS = ["area_x", "freq_x", "linewidth_x", "area_y", "freq_y", "linewidth_y", "residuals"]

# Heterodyne data was sampled every 326.613 seconds
# (Source:  UCL Data README)
SAMPLING_RATE = 1/326.613


def _process_ucl_sideband(dir, filename):
    
    """
    Load the sideband data from a .dat file. Then, create a DataFrame its contents.
    The resulting DataFrame column names are, in order:
    "area_x", "freq_x", "linewidth_x", "area_y", "freq_y", "linewidth_y", "residuals"

    Args:
        dir (str): Parent directory of the sideband data.
        filename (str):  Desired sideband data file. Must be .dat suffix.

    Returns:
        (pandas.DataFrame):  DataFrame from the contents of a sideband data file.
    """
    
    # Check that the filename specifies .dat type
    if not filename.lower().endswith(".dat"):
        raise Exception(f"{filename} must specify the `.dat` extension.")

    # Full path to the specific sideband file
    path2data = os.path.join(dir, filename)

    # Load the sideband data from .dat file into an array
    sideband_array = np.loadtxt(path2data)
    
    # Load the sideband data into a DataFrame 
    sideband_df = pd.DataFrame(data=sideband_array, columns=COLUMNS)

    return sideband_df


def _select_column(dir, filename, col_name):
    
    """
    Turn a single column of the sideband DataFrame into an array.

    Raises:
        Exception: When the supplied column name is not one of the column names.

    Args:
        dir (str): Parent directory of the sideband data.
        filename (str):  Desired sideband data file. Must be .dat suffix.
        col_name (str): The col_name an Allan deviation is being computed for.    

    Returns:
        numpy.ndarray: Column of the DataFrame as an array.
    """

    # Check that the col_name supplied is a column of the DataFrame
    if col_name not in COLUMNS:
        raise Exception(f"{col_name} not found in {COLUMNS}.")
    
    
    df = _process_ucl_sideband(dir, filename)
    
    # Select the column as a pandas.Series
    col_series = df[col_name]

    # Turn the pandas.Series into an array
    col_array = col_series.to_numpy()

    return col_array


def run_ucl_workflow(dir, filename, col_name):
    
    """
    Compute the Allan deviation of the selected column name.
    Estimate the BI, RW, and RRW of the selected column name.

    Args:
        dir (str): Parent directory of the sideband data.
        filename (str):  Desired sideband data file. Must be .dat suffix.
        col_name (str): The column name an Allan deviation is being computed for.

    Returns:
        ([numpy.ndarray, numpy.ndarray, numpy.ndarray]):  A list of the estimated coefficients.
    """
    
    # Measured signal of the time series
    signal = _select_column(dir, filename, col_name)
    
    # Compute the Allan deviation of the signal
    t, s = oadev(signal, SAMPLING_RATE)

    # Estimate the coefficients 
    bias_instability_coeff = fit_bias_instability_line(t, s)
    rate_random_walk_coeff = fit_rate_random_walk_line(t, s)
    random_walk_coeff = fit_random_walk_line(t, s)

    return bias_instability_coeff, rate_random_walk_coeff, random_walk_coeff

# End UCL