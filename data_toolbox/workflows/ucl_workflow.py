import os
import numpy as np
from data_toolbox.workflows.workflow import Workflow 
from setup import UCL_TIME_SERIES


# All UCLWorkflows navigate to these files to process their data
AREA_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "area{}.dat")
FREQ_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "f{}.dat")
SIDEBAND_PATH_TEMPLATE = os.path.join(UCL_TIME_SERIES, "fit_{}_sideband.dat")

# Split detection data is sampled every 772.26 seconds
SPLIT_DET_SAMPLING_RATE = 1/772.26

class UCLWorkflow(Workflow):

    def __init__(self):
        super().__init__()
        self.workflow_type = "UCL"
        return 

    def target_split_detection(self, mode):
        
        ## Parameter -> Area ##
        area_report = self._generate_report_from_workflow(self.workflow_type, AREA_PATH_TEMPLATE, mode, "Area under Lorentzian fit", SPLIT_DET_SAMPLING_RATE)

        ## Parameter -> Frequency ##
        freq_report = self._generate_report_from_workflow(self.workflow_type, FREQ_PATH_TEMPLATE, mode, "Mechanical Frequency", SPLIT_DET_SAMPLING_RATE)

        # Set Reports for UCLWorkflow 
        self._set_area_report(area_report)
        self._set_freq_report(freq_report)
        return
