import os
import numpy as np
import pandas as pd



def _process(dir, filename):

    """
    Load the sideband data from a .dat file. Then, create a DataFrame its contents.

    Returns:
        (pandas.DataFrame):  DataFrame from the contents of a sideband data file.
    """

    # Column names to use for the DataFrame
    COLUMNS = ["area_x", "freq_x", "linewidth_x", "area_y", "freq_y", "linewidth_y", "residuals"]
    
    # Full path to the specific sideband file
    path2data = os.path.join(dir, filename)

    # Sideband data set as an ndarray
    sideband_array = np.loadtxt(path2data)
    # Convert sideband data into a DataFrame
    return pd.DataFrame(data=sideband_array, columns=COLUMNS)



def run_workflow(dir, filename, parameter):
    pass
    return 