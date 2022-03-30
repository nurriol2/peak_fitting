import os
import numpy as np
import pandas as pd
from data_toolbox.workflows import workflow
from setup import UCL_TIME_SERIES
from data_toolbox.report import Report
from data_toolbox.workflows.workflow import Workflow 


# All UCLWorkflows navigate to these files to process their data
AREA_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "area{}.dat")
FREQ_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "f{}.dat")
SIDEBAND_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "fit_{}_sideband.dat")

# Sideband fit data contains the first six entries as column names
# The 7th entry is assumed to be an error/residuals column
# (Source:  UCL Data README)
HETR_COLUMNS = ["area_x", "freq_x", "linewidth_x", "area_y", "freq_y", "linewidth_y", "residuals"]



class UCLWorkflow(Workflow):

    def __init__(self):
        super().__init__()
        self.workflow_type = "UCL"
        return 


    # TODO:  Argument validation
    def _process_split_vec(self, filepath_template, mode):
        # Specify the split detection data to access
        data_source = filepath_template.format(mode)

        # The data serves as the output signal of a time series
        # Load the signal into an array
        signal_array = np.loadtxt(data_source)

        return (signal_array, data_source)

    def _process_hetr(self, filepath_template, which_sideband):


        # Specify the sideband data to access
        data_source = filepath_template.format(which_sideband)

        # Heterodyne data contains modal data for both sidebands arranged in a table
        # Load the table into a DataFrame
        hetr_contents = np.loadtxt(data_source)
        hetr_df = pd.DataFrame(data=hetr_contents, columns=HETR_COLUMNS)

        return hetr_df

    def _select_hetr_column(self, hetr_df, col_name):
        
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
        
        parameters = {
            "Area under Lorentzian fit (Mode:  {})": [],
            "Mechanical frequency (Mode:  {})": [],
            "Line width; FWHM of Lorentzian fit (Mode:  {})": []
        }

        for col in HETR_COLUMNS:
            if "area" in col.lower():
                parameters["Area under Lorentzian fit (Mode:  {})"].append(col)
            if "freq_" in col.lower():
                parameters["Mechanical frequency (Mode:  {})"].append(col)
            if "linewidth" in col.lower():
                parameters["Line width; FWHM of Lorentzian fit (Mode:  {})"].append(col)
        
        reverse = {}
        for k, v in parameters.items():
            for value in v:
                reverse[value] = k

        return reverse

    def target_split_detection(self, mode):

        # Split detection data is sampled every 772.26 seconds
        SPLIT_DET_SAMPLING_RATE = 1/772.26

        ## Parameter -> Area ##
        # Specify the split detection mode and the source of the data
        area_signal, area_source = self._process_split_vec(AREA_PATH_TEMPLATE, mode)
        # Compute the ADEV and calculate its coefficients
        area_coeffs = self._run_workflow(area_signal, SPLIT_DET_SAMPLING_RATE)
        # Create a report for area
        area_report = Report(
            workflow_used = self.workflow_type,
            data_source = area_source,
            parameter = f"Area under Lorentzian fit (Mode:  {mode})",
            coefficients = area_coeffs
        )

        ## Parameter -> Frequency ##
        # Specify the split detection mode and the source of the data
        freq_signal, freq_source = self._process_split_vec(FREQ_PATH_TEMPLATE, mode)
        # Compute the ADEV and calculate its coefficients
        freq_coeffs = self._run_workflow(freq_signal, SPLIT_DET_SAMPLING_RATE)
        # Create a report for area
        freq_report = Report(
            workflow_used = self.workflow_type,
            data_source = freq_source,
            parameter = f"Mechanical frequency (Mode:  {mode})",
            coefficients = freq_coeffs
        )

        ## Parameter -> Linewidth ##
        # Linewidth was not calculated in the data gathered by A & H
        # TODO:  Add linewidth analysis

        # Set Reports for UCLWorkflow 
        self._set_area_report(area_report)
        self._set_freq_report(freq_report)
        
        return

    def target_heterodyne(self, which_sideband, mode):
    
        # Heterodyne data was sampled every 326.613 seconds
        HETR_SAMPLING_RATE = 1/326.613

        PARAMETER_TEMPLATES = ["area_{}", "freq_{}", "linewidth_{}"]
        col_names = [s.format(mode) for s in PARAMETER_TEMPLATES]

        hetr_df = self._process_hetr(SIDEBAND_PATH_TEMPLATE, which_sideband)
        for col_name in col_names:
            print(f"COLUMN NAME {col_name}")
            source = SIDEBAND_PATH_TEMPLATE.format(which_sideband)
            signal = self._select_hetr_column(hetr_df, col_name)
            coeffs = self._run_workflow(signal, HETR_SAMPLING_RATE)
            parameter = self._cols2params()[col_name].format(mode)

            report = Report(
                workflow_used = self.workflow_type,
                data_source = source,
                parameter = parameter,
                coefficients = coeffs
            )

            if "area" in col_name:
                self._set_area_report(report)
            if "freq" in col_name:
                self._set_freq_report(report)
            if "linewidth" in col_name:
                self._set_line_report(report)

        return 