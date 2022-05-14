class TimeSeries:

    def __init__(self, source, ordinal_data, signal, **kwargs):

        # Time series x and y values
        self.ordinal_data = source[ordinal_data]
        self.signal = source[signal]

        # Set defaults for plotting attributes
        self.label = "Label Default"
        self.color = 'k'
        self.marker = '.'

        # Update all remaining attributes to those specified by instance
        for attr, attr_value in kwargs.items():
            self.__dict__[attr] = attr_value

        return

    def draw_on_axis(self, axis):

        """
        Wrapper for Axes.plot(...) that passes TimeSeries attribute values
        as arguments to plot()

        Args:
            axis (Axes):  Set of axes for a Figure subplot

        Example:

            # Create an `Axes` object
            fig, ax = plt.subplots()
            
            # Does the drawing
            time_series = TimeSeries(...)
            time_series.draw_on_axis(ax)

            # Shows `fig` where `ax` has the trace
            plt.show()
        """

        # Add the trace
        axis.plot(self.ordinal_data, self.signal,
                    label=self.label, color=self.color, 
                    marker=self.marker)
        axis.legend()

        return  