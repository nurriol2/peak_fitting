import os
import numpy as np
from data_toolbox.workflows.workflow import Workflow 
from data_toolbox.report import Report
from setup import UCL_TIME_SERIES


# All UCLWorkflows navigate to these files to process their data
AREA_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "area{}.dat")
FREQ_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "f{}.dat")
SIDEBAND_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "fit_{}_sideband.dat")

# Split detection data is sampled every 772.26 seconds
SPLIT_DET_SAMPLING_RATE = 1/772.26

class UCLWorkflow(Workflow):

    def __init__(self):
        self.workflow_type = "UCL"
        self.area_report = None
        self.freq_report = None
        return 

    def _set_area_report(self, report):
        self.area_report = report
        return 
    
    def _set_freq_report(self, report):
        self.freq_report = report
        return 

    # TODO:  Argument validation
    def _process_data(self, filepath_template, mode):
        # Specify the data to access
        data_source = filepath_template.format(mode)

        # The data serves as the output signal of a time series
        # Load the signal into an array
        signal_array = np.loadtxt(data_source)

        return (signal_array, data_source)
    
    def target_split_detection(self, mode):
        
        ## Parameter -> Area ##
        area_signal, area_source = self._process_data(AREA_PATH_TEMPLATE, mode)

        # Compute the ADEV and calculate coeff values
        area_coeffs = self.run_workflow(area_signal, SPLIT_DET_SAMPLING_RATE)

        # Create a Report targeting area of specified split detection mode
        area_report = Report(
            workflow_used=self.workflow_type,
            data_source=area_source,
            parameter="Area under Lorentzian fit",
            coefficients=area_coeffs
        )

        # Update the UCLWorkflow with area report
        self._set_area_report(area_report)

        ## Parameter -> Frequency ##

        return # Want to return a Report or maybe [Report, ..., Report]
