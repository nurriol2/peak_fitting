import numpy as np
import pandas as pd
from data_toolbox.report import Report
from data_toolbox.allan_func.allan import overlapping_allan_deviation as oadev
from data_toolbox.allan_func.coefficient_fitting import fit_bias_instability_line
from data_toolbox.allan_func.coefficient_fitting import fit_rate_random_walk_line
from data_toolbox.allan_func.coefficient_fitting import fit_random_walk_line


class Workflow:

    def __init__(self):
        self.area_report = None
        self.freq_report = None
        self.line_report = None
        return 


    def _set_area_report(self, report):
        self.area_report = report
        return 
    
    def _set_freq_report(self, report):
        self.freq_report = report
        return 
        

    def _run_workflow(self, signal, sampling_rate):
        # Compute the Allan deviation
        tau, sigma = oadev(signal, sampling_rate)

        # Compute the error coefficients
        # The single coefficient value is the 1th argument of the returned list
        bias_instability_coeff = fit_bias_instability_line(tau, sigma)[1]
        rate_random_walk_coeff = fit_rate_random_walk_line(tau, sigma)[1]
        random_walk_coeff = fit_random_walk_line(tau, sigma)[1]
        
        # Make coeff values selectable by name
        coeff_dict = {
            "Random Walk": random_walk_coeff,
            "Bias Instability": bias_instability_coeff,
            "Rate Random Walk": rate_random_walk_coeff
        }

        return coeff_dict


    # TODO:  Argument validation
    def _process_split_vec(self, filepath_template, mode):
        # Specify the split detection data to access
        data_source = filepath_template.format(mode)

        # The data serves as the output signal of a time series
        # Load the signal into an array
        signal_array = np.loadtxt(data_source)

        return (signal_array, data_source)

    def _process_hetr_arr(self, filepath_template, which_sideband, col_name):

        # Sideband fit data contains the first six entries as column names
        # The 7th entry is assumed to be an error/residuals column
        # (Source:  UCL Data README)
        COLUMNS = ["area_x", "freq_x", "linewidth_x", "area_y", "freq_y", "linewidth_y", "residuals"]

        # Specify the sideband data to access
        data_source = filepath_template.format(which_sideband)

        # Heterodyne data contains modal data for both sidebands arranged in a table
        # Load the table into a DataFrame
        hetr_contents = np.loadtxt(data_source)
        hetr_df = pd.DataFrame(data=hetr_contents, columns=COLUMNS)

        signal = self._select_hetr_column(hetr_df, col_name)

        return signal, data_source

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


    def _generate_report_from_workflow(self, workflow, path_template, file_desc, parameter, sampling_rate):
        
        # Define the split detection data to analyse and its location
        signal, source = self._process_split_vec(path_template, file_desc)

        # Compute the ADEV and calculate coefficient values
        coeffs = self._run_workflow(signal, sampling_rate)
        # Create a report, targeting the specified data set at source
        report = Report(
            workflow_used=workflow,
            data_source=source,
            parameter=parameter,
            coefficients=coeffs
        )

        return report