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
        return 

    # TODO:  Argument validation
    def _process_area_data(self, mode):
        # Use mode to specify the area data to access
        filepath = AREA_PATH_TEMPLATE.format(mode)

        # Load the area data into an array
        area_array = np.loadtxt(filepath)

        return area_array

    def split_detection(self, mode):
        
        # The output values of the area time series
        area_signal = self._process_area_data(mode)

        # Compute the ADEV and calculate coeff values
        self.run_workflow(area_signal, SPLIT_DET_SAMPLING_RATE)

        return # Want to return a Report or maybe [Report, ..., Report]
