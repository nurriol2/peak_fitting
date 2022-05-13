import pandas as pd
from data_toolbox.preprocessing import clean_path
import matplotlib.pyplot as plt
from matplotlib import gridspec

FIGURE_SIZE = (15, 10)

def load_complement_frames(mode, sideband=None):

    """
    Convenience function to load 2 complementary dataframes into memory.

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




def three_by_one_figure():


    fig = plt.figure(figsize=FIGURE_SIZE)
    fig.suptitle("SUPER TITLE")
    gs = gridspec.GridSpec(nrows=3, ncols=1, hspace=0.5, left=0.05, right=0.98)
    left_plot = fig.add_subplot(gs[0])
    center_plot = fig.add_subplot(gs[1])
    right_plot = fig.add_subplot(gs[2])
    
    titles = ("left", "center", "right")
    xlabels = ("left", "center", "right")
    ylabels = ("left", "center", "right")


    annotate_axes(fig, titles, xlabels, ylabels)

    import numpy as np
    foo_x = np.arange(124)
    foo_y = np.random.rand(124,)
    bar_y = np.random.rand(124,) + 10

    for pos_n, axis in enumerate([left_plot, center_plot, right_plot]):
        populate_axis(axis, foo_x, foo_y, pos_n, pos_n)
        populate_axis(axis, foo_x, bar_y, pos_n+1%3, pos_n)

    plt.show()

    return 

def annotate_axes(fig, titles, xlabels, ylabels):

    for i, ax in enumerate(fig.axes):
        ax.set_title(f"{titles[i]}")
        ax.set_xlabel(f"{xlabels[i]}")
        ax.set_ylabel(f"{ylabels[i]}")
        ax.legend()

    return 

def populate_axis(axis, time, signal, label, pos_n):

    color = ('k', 'r', 'g')
    marker = ('o', 's', 'P')



    axis.plot(time, signal, label=label, color=color[pos_n], marker=marker[pos_n])


    return 