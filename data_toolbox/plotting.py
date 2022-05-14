import matplotlib.pyplot as plt
from matplotlib import gridspec


def annotate_axis(axis, title, xlabel, ylabel):

    """
    Utility to set subplot title, xlabel, and ylabels.

    Args:
        axis (Axes):  Set of axes for a Figure subplot

        title (str):  Title of the subplot

        xlabel(str):  Subplot's x-axis label

        ylabel(str):  Subplot's y-axis label
    """

    axis.set_title(title)
    axis.set_xlabel(xlabel)
    axis.set_ylabel(ylabel)   

    return 


def three_by_one(comparison_name):
    """
    Utility for building a figure of time series subplots.
    The subplots are stacked vertically (3 subplots in 1 col)

    Args:
        comparison_name (str): Title of the Figure

    Returns:
        tuple(Figure, Axes, Axes, Axes): Return a tuple of plot objects.
                                         Figure is the figure containing subplots.
                                         Each set of Axes is a subplot that a trace can be added to.

    Example:
        
        # Initialize a Figure and its subplots (axes)
        fig, tax, cax, bax = three_by_one("My Stacked Plot")
        
        # Annotate each axis with axis labels and subplot title
        annotate_axis(tax, ...)
        annotate_axis(cax, ...)
        annotate_axis(bax, ...)

        ### Draw TimeSeries traces on the axis ###
        # Put a time series on the top axis
        time_series_1.draw_on_axis(tax)
        # Put 2 different time series on the center axis
        time_series_2.draw_on_axis(cax)
        time_series_3.draw_on_axis(cax)
        # Leave the bottom axis blank
        # (do nothing to `bax`)

    """
     
    FIGURE_SIZE = (15, 10)
    fig = plt.figure(figsize=FIGURE_SIZE)
    fig.suptitle(f"{comparison_name}")
    
    # Create the 3x1 subplot grid
    # Subplot spacing and area look good for the 124 data points in the current data set
    gs = gridspec.GridSpec(nrows=3, ncols=1, hspace=0.5, left=0.08, right=0.98)
    top_plot = fig.add_subplot(gs[0])
    center_plot = fig.add_subplot(gs[1])
    bot_plot = fig.add_subplot(gs[2])

    return (fig, top_plot, center_plot, bot_plot)

