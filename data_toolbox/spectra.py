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

    # Area under the spectrum
    raw_area: float = field(init=False)
    # Initial estimates for the widths of each peak
    left_width:  float = field(init=False)
    right_width: float = field(init=False)
    main_width: float = field(init=False)
    

    def __post_init__(self):
        super().__post_init__()
        self._set_width_estimates()
        return


    def _set_width_estimates(self):
        estimates = peak_widths(self.spectrum, self._peak_selection(), rel_height=0.5)
        values = estimates[0]
        self.left_width = values[0]
        self.main_width = values[1]
        self.right_width = values[2]
        return 


    def _peak_selection(self):
        # Locate peaks in the spectrum by index
        peak_indices, _ = find_peaks(self.spectrum)
        # Select corresponding amplitudes of found peaks
        peak_amplitudes = self.spectrum[peak_indices]
        
        # Sort the peaks according to height; largest to smallest
        amp_idx_pairs = list(zip(peak_amplitudes, peak_indices)) 
        amp_idx_pairs.sort(key=lambda pair : pair[0], reverse=True)

        # Track the left and right side peaks
        left_idx = None
        right_idx = None

        # Main peak is always the tallest
        main_amp, main_idx = amp_idx_pairs[0]

        # The next tallest peak should appear on one side of the main peak
        side_a_amp, side_a_idx = amp_idx_pairs[1]

        # The opposite side peak depends on where side_a peak is located
        side_b_pair = None
        # The side_a peak was left of the main peak
        if side_a_idx < main_idx:
            left_idx = side_a_idx
            # Compare indices to find the tallest peak on the right of the main peak
            right_idx = (next(pair[1] for pair in amp_idx_pairs[2:] if pair[1] > main_idx))
        # The side_a peak was right of the main peak
        else:
            right_idx = side_a_idx
            # Compare indices to find the tallest peak on the left of the main peak
            left_idx = (next(pair[1] for pair in amp_idx_pairs[2:] if pair[1] < main_idx))

        return (left_idx, main_idx, right_idx)


    def fit_right_peak(self, tune=0.75):
        """
        Note:   This function will irreversibly mutate the HetrodyneData object.
                Create a new HeteroDyne object to fit main or left peaks.
        """

        _, main_loc, right_loc = self._peak_selection()
        # Find the frequency that escapes main peak influence
        escape_index = int(main_loc + tune*(right_loc-main_loc))
        # Trim the spectrum according to `escape_index`
        trim_low = self.frequencies[escape_index]
        self.trim_data(low=trim_low)
        
        # Right index has the property that it's distance from end of array is constant
        dyn_right_loc = -1*(len(self.frequencies)-right_loc)
        # Initial guess for Lorentzian
        right_guess = [self.spectrum[dyn_right_loc],
                       self.frequencies[dyn_right_loc],
                       self.right_width,
                       self.spectrum.min()]

        def _1Lorentzian(x, amp, cen, wid, back):
            return (amp*wid**2/((x-cen)**2+wid**2))+back

        # Fit Lorentzian parameters
        right_optimal_params, _ = scipy.optimize.curve_fit(_1Lorentzian,
                                                           self.frequencies,
                                                           self.spectrum,
                                                           p0=right_guess,
                                                           maxfev=5000)

        return Lorentzian(self.frequencies, *right_optimal_params)

    def fit_left_peak(self, tune=0.40):
        """
        Note:   This function will irreversibly mutate the HetrodyneData object.
                Create a new HeteroDyne object to fit main or right peaks.
        """

        left_loc, main_loc, _ = self._peak_selection()
        # Find the frequency that escapes main peak influence
        escape_index = int(main_loc - tune*(main_loc-left_loc))
        # Trim the spectrum according to `escape_index`
        trim_high = self.frequencies[escape_index]
        self.trim_data(high=trim_high)
        
        # Left index has the property that it's distance from start of array is constant
        # Initial guess for Lorentzian
        left_guess = [self.spectrum[left_loc],
                       self.frequencies[left_loc],
                       self.left_width,
                       self.spectrum.min()]

        def _1Lorentzian(x, amp, cen, wid, back):
            return (amp*wid**2/((x-cen)**2+wid**2))+back

        # Fit Lorentzian parameters
        left_optimal_params, _ = scipy.optimize.curve_fit(_1Lorentzian,
                                                           self.frequencies,
                                                           self.spectrum,
                                                           p0=left_guess,
                                                           maxfev=5000)

        return Lorentzian(self.frequencies, *left_optimal_params)
# End HeterodyneData