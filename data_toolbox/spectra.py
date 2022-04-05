import os
import scipy
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from data_toolbox.lorentz import Lorentzian
from scipy.signal import find_peaks, peak_widths

@dataclass
class SpectrumFile:
    """
    Class for working with sideband and heterodyne spectral density measurements
    """

    directory: str
    pattern: str
    units: str
    fullpath: str = field(init=False)
    frequencies: np.ndarray = field(init=False)
    spectrum: np.ndarray = field(init=False)

    def __post_init__(self):
        self.fullpath = os.path.join(self.directory, self.pattern)
        self.frequencies, self.spectrum = self.file_to_arrays()
        return 


    def _load_csv_file(self):
        """
        Load a single csv file into memory as a pandas.DataFrame
        
        Returns:
        (pd.DataFrame):  A pandas.DataFrame where the columns are Frequency (Hz)
                         and Spectral Density (...) with specified units.
        """

        return pd.read_csv(self.fullpath, names=["Frequency (Hz)", f"Spectral Density ({self.units})"])


    def _columns_to_array(self, df):
        """
        Create individual numpy arrays from columns of a data frame

        Args:
        df (pd.DataFrame):  The data frame to convert

        Returns:
        tuple(np.array, ... np.array):  The columns of `df` as elements of a tuple.
                                        Length of tuple depends on number of columns.
        """
        result = []
        for _, col_data in df.iteritems():
            result.append(col_data.values)
        return result


    def file_to_arrays(self):

        """
        Process a single spectrum file into memeory as numpy arrays

        Returns:
        tuple(np.array, ... np.array):  The columns of `df` as elements of a tuple.
                                        Length of tuple depends on number of columns.
        """

        df = self._load_csv_file()

        return self._columns_to_array(df)    


    def sort_key(self):
        """
        Find the file number from the path to a file.
        Example:  Extract the number 109 from /.../cha_st80_109.CSV

        Args:
        fullpath (str):  The full path to the CSV file

        Returns:
        (int):  The found file number
        """

        filename = self.fullpath.split('/')[-1]
        filenumber = filename.split('_')[-1].strip(".CSV")
        return filenumber   
        
    def trim_data(self, low=None, high=None):
        """
        Set the low and high frequency of the SpectrumFile object in place.
        Trim the spectrum array to the corresponding values.
        """
        
        # Call without parameters should return the original array
        low_index = 0
        high_index = len(self.frequencies)-1
        
        # Determine the index of the element closest to value
        # If multiple matches, takes the first occurance 
        close_elem_index = lambda array, value : np.absolute(array-value).argmin()
        
        if low is not None:
            low_index = close_elem_index(self.frequencies, low)
        if high is not None:
            high_index = close_elem_index(self.frequencies, high)
        
        self.frequencies = self.frequencies[low_index:high_index+1]
        self.spectrum = self.spectrum[low_index:high_index+1]
        return 

# End SpectrumFile



@dataclass
class SplitDetectionData(SpectrumFile):
    """
    Class for working with split detection data.
    Example:  `cha_st80_1.CSV`
    """

    # Area under the spectrum
    raw_area: float = field(init=False)
    # Initial estimate for the width of the peak
    width_estimate: float = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self._set_width_estimate()
        self.raw_area = np.trapz(self.spectrum)
        return

    # TODO:  Associate width with the Lorentzian object?
    def _set_width_estimate(self):    
        estimate = peak_widths(self.spectrum, [np.argmax(self.spectrum)], rel_height=0.5)
        self.width_estimate = estimate[0].item(0)
        return

    def init_lorentzian(self):
        """
        Define a Lorentzian object from frequency and spectrum data
        """ 

        def _1Lorentzian(x, amp, cen, wid, back):
            return (amp*wid**2/((x-cen)**2+wid**2))+back
        
        # Frequency of peak
        center = self.frequencies[np.where(self.spectrum==self.spectrum.max())].item()
        
        optimal_params, _ = scipy.optimize.curve_fit(_1Lorentzian,
                                                    self.frequencies,
                                                    self.spectrum,
                                                    p0=[self.spectrum.max().item(),
                                                        center,
                                                        self.width_estimate,
                                                        self.spectrum.min().item()])

        return Lorentzian(self.frequencies, *optimal_params)

# End SplitDetectionData



@dataclass
class HeterodyneData(SpectrumFile):
    """
    Class for working with heterodyne data.
    Example:  `het_st80_1.CSV`

    NB: Scipy's optimize module has been shown to fit multiple peaks with less
        error than a composite model from LMFIT. For this use case, we only care
        about the measurements of the fit (e.g. FWHM, mechanical frequency, linewidth).
    """  

    def _assign_left_and_right(self, tall_to_short):
        """
        Calculate the index of the prominent side peaks

        Args:
            tall_to_short (list(tuple)): List of (amplitude, index) pairs sorted by amplitude in descending order.

        Returns:
            tuple(int, int): The index of the left and right prominent peaks, respectively.
        """

        # Assume the center peak is the tallest peak
        _, center_idx = tall_to_short[0]


        # Tallest peak on the left of the center peak
        #   Look through the remaining peaks for the first instance of an index below the center index
        left_idx = (next(pair[1] for pair in tall_to_short[1:] if pair[1] < center_idx))
        # Tallest peak on the right of the center peak 
        #   Look through the remaining peaks for the first instance of an index above the center index
        right_idx = (next(pair[1] for pair in tall_to_short[1:] if pair[1] > center_idx))

        return (left_idx, right_idx)

    def _find_partition_range(self):

        """
        Determine the range of indices that can be used to partition the spectrum
        into 2 regions. One region for the positive sideband and another for the
        negative sideband.

        It's suggested that the resulting ranges are "tuned" before trimming.

        Returns:
            dict: Dictionary containing ranges for each sideband. 
                  Each range is given as a tuple; (start index, end index)
                  Keys:  "pos", "neg".
        """

        # Starting index of the negative sideband
        START = 0
        # Ending index of the positive sideband
        END = len(self.spectrum)-1

        # Get an array of indices corresponding to peaks in the spectrum
        peak_indices, _ = find_peaks(self.spectrum)
        # Get the amplitude of the found peaks
        peak_amplitudes = self.spectrum[peak_indices]
        # Create (peak amplitude, peak index) pairs
        peak_amp_idx_pairs = list(zip(peak_amplitudes, peak_indices))
        # Sort the peaks according to height (tallest to shortest)
        peak_amp_idx_pairs.sort(key = lambda pair: pair[0], reverse=True)

        # Get a rough estimate of the partition indices
        # For the positive sideband, the right index is a starting index
        # For the negative sideband, the left index is an ending index
        left_idx, right_idx = self._assign_left_and_right(peak_amp_idx_pairs)
        # Create the partition
        partition = {
            "neg":(START, left_idx),
            "pos":(right_idx, END)
        }

        return partition

    def _choose_peak(self, which_sideband, mode):
        
        """
        Determine which peak to fit according to the sideband and directional mode.
        This method assumes the spectrum has already been trimmed to focus on a
        sideband. 

        Example:

        # Create the SpectrumFile object
        hetr = HeterodyneData(...)
        # Trim the data to focus on the negative sideband
        hetr.trim_spectrum_to_sideband("neg", 200, -1_000)
        # Locate the y-directional mode peak
        y_mode = hetr._choose_peak("neg", 'y')


        Returns:
            int: The index of the desired peak.
        """

        # Find peaks in the sideband
        peak_idxs, _ = find_peaks(self.spectrum)
        # Widths of the found peaks
        wids = peak_widths(self.spectrum, peak_idxs)[0]
        # Sort the found peaks according to widths in descending order
        sorted_wids = list(zip(wids, peak_idxs))
        sorted_wids.sort(key = lambda pair: pair[0], reverse=True)
        # Assume the two widest peaks in this sideband are the peaks to fit
        target_peaks = sorted_wids[0:2]
        idx_a, idx_b = [p[1] for p in target_peaks]
     
        # Determine the peak to fit according to chosen sideband and the directional mode     
        peak_idx = None
        if (which_sideband == "pos") and (mode == 'x'):
            peak_idx = min(idx_a, idx_b)
        elif (which_sideband == "pos") and (mode == 'y'):
            peak_idx = max(idx_a, idx_b)
        elif (which_sideband == "neg") and (mode == 'x'):
            peak_idx = max(idx_a, idx_b)
        elif (which_sideband == "neg") and (mode == 'y'):
            peak_idx = min(idx_a, idx_b)

        return peak_idx


    def trim_spectrum_to_sideband(self, which_sideband, tune_start=0, tune_end=0):
        """
        Adjust the estimated start and ending indices of the sideband.
        Trim the full spectrum so that only the selected sideband remains.


        Args:
            which_sideband (str): The sideband to select. 
                                  Either "pos" for the region right of the center peak or
                                  "neg" for the region left of the center peak.
            tune_start (int, optional): The number of indices to adjust the starting index. 
                                        Defaults to 0.
            tune_end (int, optional): The number of indices to adjust the ending index. 
                                      Defaults to 0.
        """

        # Get the pos/neg sideband ranges
        partition = self._find_partition_range()
        # Choose indices for desired sideband
        start_idx, end_idx = partition[which_sideband]
        # Tune the indices
        start_idx += tune_start
        end_idx += tune_end
        # Translate indices to frequency
        low = self.frequencies[start_idx]
        high = self.frequencies[end_idx]
        # Trim the data starting and ending at the specified frequencies
        self.trim_data(low=low, high=high)

        return



      

# End HeterodyneData