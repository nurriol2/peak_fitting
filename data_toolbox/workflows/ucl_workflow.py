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
        return 

    def _set_area_report(self, report):
        self.area_report = report
        return 

    # TODO:  Argument validation
    def _process_area_data(self, mode):
        # Use mode to specify the area data to access
        filepath = AREA_PATH_TEMPLATE.format(mode)

        # Load the area data into an array
        area_array = np.loadtxt(filepath)

        return (area_array, filepath)

    def split_detection(self, mode):
        
        ## Parameter -> Area ##
        # Area values as the output of a time series in an array
        # The filepath indicating the source of the data
        area_signal, filepath = self._process_area_data(mode)

        # Compute the ADEV and calculate coeff values
        area_coeffs = self.run_workflow(area_signal, SPLIT_DET_SAMPLING_RATE)

        # Create a Report targeting area of specified split detection mode
        area_report = Report(
            workflow_used=self.workflow_type,
            data_source=filepath,
            parameter="area",
            coefficients=area_coeffs
        )

        # Update the UCLWorkflow
        self._set_area_report(area_report)

        ## Parameter -> Frequency ##

        return # Want to return a Report or maybe [Report, ..., Report]
