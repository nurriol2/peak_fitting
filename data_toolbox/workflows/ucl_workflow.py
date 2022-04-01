import os
import numpy as np
import pandas as pd
from setup import UCL_TIME_SERIES, HETR_SAMPLING_RATE, SPLIT_DET_SAMPLING_RATE
from data_toolbox.report import Report
from data_toolbox.workflows.workflow import Workflow 



# All UCLWorkflows navigate to these files to process their data
AREA_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "area{}.dat")
FREQ_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "f{}.dat")
SIDEBAND_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "fit_{}_sideband.dat")

# Sideband fit data contains the first six entries as column names
# The 7th entry is assumed to be an error/residuals column
HETR_COLUMNS = ["area_x", "freq_x", "linewidth_x", "area_y", "freq_y", "linewidth_y", "residuals"]



class UCLWorkflow(Workflow):
    """
    Subclass to extract Allan deviation noise coefficients using the fit data already obtained by UCL researchers.
    `UCLWorkflow` inherits from `Workflow` class.
    """

    def __init__(self):
        super().__init__()
        self.workflow_type = "UCL"
        return 


    # TODO:  Argument validation
    def _process_split_vec(self, filepath_template, mode):

        """
        Load a 1-dimensional vector into an array. 
        Report the source of this data.

        Args:
            filepath_template (str): Full path leading to the source of the data.
            mode (str): Directional mode of the data. Either 'x' or 'y'.

        Returns:
            numpy.ndarray: The contents of the vector as an array.
        """

        # Specify the split detection data to access
        data_source = filepath_template.format(mode)

        # The data serves as the output signal of a time series
        # Load the signal into an array
        signal_array = np.loadtxt(data_source)

        return (signal_array, data_source)

    def _process_hetr(self, filepath_template, which_sideband):
        
        """
        Load a multi-dimensional array as a DataFrame with specified column names.

        Args:
            filepath_template (str): Full path leading to the source of the data.
            which_sideband (str): Key that specifies which sideband fit data to use.

        Returns:
            pandas.DataFrame: The contents of heterodyne data as a DataFrame.
        """

        # Specify the sideband data to access
        data_source = filepath_template.format(which_sideband)

        # Heterodyne data contains modal data for both sidebands arranged in a table
        # Load the table into a DataFrame
        hetr_contents = np.loadtxt(data_source)
        hetr_df = pd.DataFrame(data=hetr_contents, columns=HETR_COLUMNS)

        return hetr_df


    def _select_hetr_column(self, hetr_df, col_name):
        """
        Select a single column of a DataFrame and return it as an array.

        Args:
            hetr_df (pandas.DataFrame): The contents of heterodyne data as a DataFrame.
            col_name (str): The column name used to select a column from the DataFrame.

        Raises:
            Exception: If the provided column name is not a column of the DataFrame.

        Returns:
            numpy.ndarray: The specified DataFrame column as an array.
        """
        
        # Check that the selection is a valid column name
        valid_col_names = list(hetr_df.columns)
        if col_name not in valid_col_names:
            raise Exception(f"{col_name} not found in {valid_col_names}")

        # Select the column as a panda.Series
        selected_col = hetr_df[col_name]
        
        # Values to return
        signal = selected_col.to_numpy()

        return signal


    def _cols2params(self):
        """
        Create a dict to progromatically assign `feature` based on the column name.

        Returns:
            dict: Keys are potential column names for heterodyne data. Values are `feature` strings used for `Report`s
        """
        
        # Start with the keys and values reversed from desired format
        features = {
            "Area under Lorentzian fit (Mode:  {})": [],
            "Mechanical frequency (Mode:  {})": [],
            "Line width; FWHM of Lorentzian fit (Mode:  {})": []
        }

        # Add column names to corresponding value based on their contents
        for col in HETR_COLUMNS:
            if "area" in col.lower():
                features["Area under Lorentzian fit (Mode:  {})"].append(col)
            if "freq_" in col.lower():
                features["Mechanical frequency (Mode:  {})"].append(col)
            if "linewidth" in col.lower():
                features["Line width; FWHM of Lorentzian fit (Mode:  {})"].append(col)
        
        # The dictionary to be returned
        reverse = {}
        # Reverse the dictionary that was just populated
        for k, v in features.items():
            # Unpack the list of colum names
            for value in v:
                # Use the colum names as keys and `feature`s as values
                reverse[value] = k

        return reverse


    def target_split_detection(self, mode):

        """
        Automate `Report` generation for all split detection data `feature`s in the given mode.

        Args:
            mode (str): Directional mode of the data. Either 'x' or 'y'.
        """ 

        ## feature -> Area ##
        # Specify the split detection mode and the source of the data
        area_signal, area_source = self._process_split_vec(AREA_PATH_TEMPLATE, mode)
        # Compute the ADEV and calculate its coefficients
        area_coeffs = self._run_workflow(area_signal, SPLIT_DET_SAMPLING_RATE)
        # Create a report for area
        area_report = Report(
            workflow_used = self.workflow_type,
            data_source = area_source,
            feature = f"Area under Lorentzian fit (Mode:  {mode})",
            coefficients = area_coeffs
        )

        ## feature -> Frequency ##
        # Specify the split detection mode and the source of the data
        freq_signal, freq_source = self._process_split_vec(FREQ_PATH_TEMPLATE, mode)
        # Compute the ADEV and calculate its coefficients
        freq_coeffs = self._run_workflow(freq_signal, SPLIT_DET_SAMPLING_RATE)
        # Create a report for area
        freq_report = Report(
            workflow_used = self.workflow_type,
            data_source = freq_source,
            feature = f"Mechanical frequency (Mode:  {mode})",
            coefficients = freq_coeffs
        )

        ## feature -> Linewidth ##
        # Linewidth was not calculated in the data gathered by A & H
        # TODO:  Add linewidth analysis

        # Set Reports for UCLWorkflow 
        self._set_area_report(area_report)
        self._set_freq_report(freq_report)
        
        return

    def target_heterodyne(self, which_sideband, mode):
        """
        Automate `Report` generation for all heterodyne data `feature`s in the specified mode.
        Since heterodyne data is multi-dimensional, processing depends on the colum names found
        in the DataFrame.

        Args:
            which_sideband (str): Sideband to analyze. Either "neg" or "pos".
            mode (str): Directional mode of the data. Either 'x' or 'y'.
        """

        # Templates for the possible column names found in the DataFrame
        feature_TEMPLATES = ["area_{}", "freq_{}", "linewidth_{}"]
        # Use the specified mode to format the `feature`s
        col_names = [s.format(mode) for s in feature_TEMPLATES]

        # Create a DataFrame from the heterodyne data
        # Specify which sideband to use
        hetr_df = self._process_hetr(SIDEBAND_PATH_TEMPLATE, which_sideband)
        # Loop through the specified column names
        for col_name in col_names:
            # Source of heterodyne sideband fit data
            source = SIDEBAND_PATH_TEMPLATE.format(which_sideband)
            # Area, frequency, or linewidth signal as a time series
            signal = self._select_hetr_column(hetr_df, col_name)
            # Compute coefficients from the Allan deviation
            coeffs = self._run_workflow(signal, HETR_SAMPLING_RATE)
            # Look up what the `feature` should be 
            feature = self._cols2params()[col_name].format(mode)

            # Generate a `Report` to package all the information
            report = Report(
                workflow_used = self.workflow_type,
                data_source = source,
                feature = feature,
                coefficients = coeffs
            )

            # Update the `UCLWorkflow` according to which `feature` was just analyzed
            if "area" in col_name:
                self._set_area_report(report)
            if "freq" in col_name:
                self._set_freq_report(report)
            if "linewidth" in col_name:
                self._set_line_report(report)

        return 