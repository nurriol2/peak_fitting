import pandas as pd
import matplotlib.pyplot as plt
import data_toolbox.constants as constants
from setup import build_file_tree
from data_toolbox.time_series import TimeSeries
from data_toolbox.plotting import annotate_axis, three_by_one
from data_toolbox.preprocessing import clean_path, ready_all_cst, ready_all_ucl

def load_complement_frames(mode, sideband=None):

    """
    Utility to load 2 complementary dataframes into memory.

    Comparable frames always have the same identifiers.

    Args:
        mode (str):  Directional mode identifier for the clean filename template.
                     Must be either 'x' or 'y'

        sideband (str, optional):  Sideband identifier for the clean filename template.
                                   If "positive" or "negative", opens `clean_data/heterodyne/` subidirectory.
                                   If None, opens `clean_data/split_detection/` subdirectory.
                                   Defaults to None.

    Returns:
        tuple(pandas.DataFrame, pandas.DataFrame): A tuple of frames. The order is (UCL frame, CST frame).
    """

    ucl_df = pd.read_csv(clean_path(source="ucl", mode=mode, sideband=sideband))
    cst_df = pd.read_csv(clean_path(source="cst", mode=mode, sideband=sideband))

    return (ucl_df, cst_df)


def write_comparison_name(mode, sideband):

    """
    Utility to automatically format the comparison name depending on the mode and sideband.

    Returns:
        (str): Formatted comparison string.
    
    Example:
        comparison_name = write_comparison_name(mode=mode, sideband=sideband)
        _, tax, cax, bax = three_by_one(comparison_name=comparison_name)
    """

    comparison_name = None

    # Indicates Split Detection data
    if sideband is None:
        comparison_name = f"Split Detection Measurement:  {mode} Directional Mode"
    # Only heterodyne measurements have sidebands
    else:
        comparison_name = f"Heterodyne Measurement:  {mode} Directional Mode of {sideband} Sideband"

    return comparison_name


def plot_full_comparison(mode, sideband=None):

    """
    Iterate over combinations of directional mode and sideband. 
    Generate a full (3 plots x 1 col) comparison plots of the feature time series.

    Args:
        mode (str):  Directional mode identifier. 
                     Can be either 'x' or 'y'.
        
        sideband (str):  Sideband identifier. Can be either "positive" or "negative".
                         Defaults to None.
    """

    # Load complementary data
    udf, cdf = load_complement_frames(mode=mode, sideband=sideband)
    
    # Determine the units of area under curve
    units = constants.HETERODYNE_UNITS
    if sideband is None:
        units = constants.SPLIT_DETECTION_UNITS

    ### Create time series from the data ###
    # Area under Lorentzian
    ucl_aoc = TimeSeries(udf, "time_step", "area_under_curve",
                        label="UCL", color='r')
    cst_aoc = TimeSeries(cdf, "time_step", "area_under_curve",
                        label="CST", color='g')
    # Mechanical frequency
    ucl_freq = TimeSeries(udf, "time_step", "mechanical_frequency",
                        label="UCL", color='r')
    cst_freq = TimeSeries(cdf, "time_step", "mechanical_frequency",
                        label="CST", color='g')
    # Linewidth (using any available data)
    ucl_lin = TimeSeries(udf, "time_step", "linewidth",
                        label="UCL", color='r')
    cst_lin = TimeSeries(cdf, "time_step", "linewidth",
                        label="CST", color='g')


    # Set up the plotting elements
    comparison_name = write_comparison_name(mode=mode, sideband=sideband)
    _, tax, cax, bax = three_by_one(comparison_name=comparison_name)
    # Annotate each of the subplots
    annotate_axis(tax, "Area Under Lorentzian", "Time (sec)", f"Area ({units})")
    annotate_axis(cax, "Mechanical Frequency", "Time (sec)", "Frequency (Hz)")
    annotate_axis(bax, "Lorentzian Linewidth", "Time (sec)", "Linewidth (Hz)")


    # Draw traces on subplots
    ucl_aoc.draw_on_axis(tax)
    ucl_freq.draw_on_axis(cax)
    ucl_lin.draw_on_axis(bax)

    cst_aoc.draw_on_axis(tax)
    cst_freq.draw_on_axis(cax)
    cst_lin.draw_on_axis(bax)


    # Show the full comparison plot
    plt.show()

    return

def main():

    # These need to run once to preprocess the raw data into clean data
    # After that, they only serve to slow the code down
    # So, they are commented out in subsequent calls to `main`
    # TODO:  Make these calls conditional
    # build_file_tree()
    # ready_all_ucl()
    # ready_all_cst()

    # TODO:  Add figure saving flag
    split_detection_comparisons = [('x', None), ('y', None)]
    heterodyne_comparisons = [('x', "positive"), ('x', "negative"), ('y', "positive"), ('y', "negative")]

    for mode, sideband in heterodyne_comparisons:
        plot_full_comparison(mode=mode, sideband=sideband)

    for mode, sideband in split_detection_comparisons:
        plot_full_comparison(mode=mode, sideband=sideband)

    return

if __name__=="__main__":
    main()