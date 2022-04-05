from multiprocessing.sharedctypes import Value
import os
import numpy as np
from data_toolbox.report import Report
from data_toolbox.spectra import SplitDetectionData, HeterodyneData
from data_toolbox.workflows.workflow import Workflow
from setup import SPLIT_DETECTION_RAW, HETERODYNE_RAW, HETR_SAMPLING_RATE, SPLIT_DET_SAMPLING_RATE


# Raw experiment data files follow these templates
CHA_ST80_TEMPLATE = "cha_st80_{}.CSV"
CHB_ST80_TEMPLATE = "chb_st80_{}.CSV"
HET_ST80_TEMPLATE = "het_st80_{}.CSV"
# Units for both split detection and heterodyne data
SPLIT_DET_UNITS = "m^2/Hz"
HETR_UNITS = "V^2/Hz"


class CustomWorkflow(Workflow):
    """
    Subclass to extract Allan deviation noise coefficients.
    `CustomWorkflow` processes raw experiment data by fitting a Lorentzian curve according
    to a custom fitting procedure implemented in `data_toolbox`. 
    `CustomWorkflow` inherits from `Workflow`.
    """

    def __init__(self):
        super().__init__()
        self.workflow_type = "Custom"
        return


    def _build_time_series(self, lorentzians):
        signals = []
        for lorentzian in lorentzians:
            signals.append(lorentzian.all_values())
        area_signal = np.array([d["fit_area"] for d in signals])
        freq_signal = np.array([d["mechanical_frequency"] for d in signals])
        line_signal = np.array([d["linewidth"] for d in signals])
        return (area_signal, freq_signal, line_signal)

    def _generate_multiple_reports(self, lorentzians, dir, templ, flag, sampling_rate):
        
        # Each Lorentzian object carries one element from each of the 3 time series
        # Map between the time series order and the `feature` it corresponds to
        feature_map = {
            0:"Area under Lorentzian fit (Mode:  {})",
            1:"Mechanical frequency (Mode:  {})",
            2:"Line width; FWHM of Lorentzian fit (Mode:  {})"
        }

        # Enumerate the time series
        for key, signal in enumerate(self._build_time_series(lorentzians)):
            # Set up `Report` attributes
            workflow_used = self.workflow_type
            data_source = os.path.join(dir, templ)
            feature = feature_map[key].format(flag)
            # Actually calcualte the ADEV and coefficients here
            coefficients = self._run_workflow(signal, sampling_rate)

            # Generate a `Report` with the appropriate `feature`
            if key == 0:
                report = Report(
                    workflow_used = workflow_used,
                    data_source = data_source,
                    feature = feature,
                    coefficients = coefficients
                )
                self._set_area_report(report)
            
            if key == 1:
                report = Report(
                    workflow_used = workflow_used,
                    data_source = data_source,
                    feature = feature,
                    coefficients = coefficients
                )
                self._set_freq_report(report)
            
            if key == 2:
                report = Report(
                    workflow_used = workflow_used,
                    data_source = data_source,
                    feature = feature,
                    coefficients = coefficients
                )
                self._set_line_report(report)
        return 

    # TODO:  Programatically determine nFiles
    def target_split_detection(self, mode, nFiles=124):

        # Translate the mode into the corresponding filename template
        file_map = {
            'x':CHA_ST80_TEMPLATE,
            'y':CHB_ST80_TEMPLATE
        }
        
        # Set the filename template
        file_template = file_map[mode]

        # Accumulate a list of Lorentzian objects
        lorentzians = []
        # Loop over each of the CSV data files
        for i in range(1, nFiles+1):
            split_det_file = SplitDetectionData(SPLIT_DETECTION_RAW, file_template.format(i), SPLIT_DET_UNITS)
            # SplitDetectionData have a single peak Lorentzian profile
            # Fit a single peak Lorentzian to the data and add it to the list
            lorentzians.append(split_det_file.init_lorentzian())

        self._generate_multiple_reports(lorentzians, SPLIT_DETECTION_RAW, file_template, mode, SPLIT_DET_SAMPLING_RATE)

        return 


    def target_heterodyne(self, which_sideband, mode, nFiles=124):

        # Hueristics for getting the best window into the sideband
        NEG_START_ADJ = 200
        NEG_END_ADJ = -1_000
        POS_START_ADJ = 1_000

        lorentzians = []
        for i in range(1, nFiles+1):
            # Create a HeterodyneData object for each file in the directory
            hetr_file = HeterodyneData(HETERODYNE_RAW, HET_ST80_TEMPLATE.format(i), HETR_UNITS)

            # Tune the sideband window
            if which_sideband == "pos":
                hetr_file.trim_spectrum_to_sideband(which_sideband, POS_START_ADJ)
            elif which_sideband == "neg":
                hetr_file.trim_spectrum_to_sideband(which_sideband, NEG_START_ADJ, NEG_END_ADJ)       
            # Selected sideband is not an option
            else:
                raise ValueError(f"`{which_sideband}` is not a sideband. Must be 'pos' or 'neg'.")
            
            lorentzians.append(hetr_file.fit_lorentzian(which_sideband, mode))

        self._generate_multiple_reports(lorentzians, HETERODYNE_RAW, HET_ST80_TEMPLATE, mode, HETR_SAMPLING_RATE)

        return 