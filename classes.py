# Define classes

import os
import numpy as np
import pandas as pd
import scipy as scipy
from scipy.signal import find_peaks
from dataclasses import dataclass, field
from lmfit.models import ConstantModel, LorentzianModel

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
        self.frequencies, self.spectrum = self.spectrum_to_arrays()
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


    def spectrum_to_arrays(self):

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
class SplitBandData(SpectrumFile):
    """
    Class for working with split band data.
    Example:  `cha_st80_1.CSV`
    """

    # Attributes that eventually become the data for ADEV
    raw_area: float = field(init=False)
    fit_area: float = field(init=False)
    mechanical_frequency: float = field(init=False)
    linewidth: float = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        return


    def fit_1d_lorentzian(self):
        """
        Fit a single peak Lorentzian to the spectrum.
        Use the resulting Lorentzian to compute:
            raw_area:  Area under the spectrum 
            fit_area:  Area under the best fit Lorentzian curve
            mechanical_frequency: Amplitude of the center peak
            linewidth:  Full width at half maximum (FWHM)
        """
        # Define components of the model
        background = ConstantModel()
        peak = LorentzianModel()

        # Define model parameters
        pars = background.make_params(c=self.spectrum.min())
        pars += peak.guess(self.spectrum, x=self.frequencies)

        # Build the model
        model = peak + background

        # Find the best fit Lorentzian
        lorentzian_result = model.fit(self.spectrum, pars, x=self.frequencies)
        
        # Use the best fit Lorentzian to calculate desired values
        self.fit_area = np.trapz(lorentzian_result.best_fit)
        self.mechanical_frequency = lorentzian_result.best_values["amplitude"]
        self.linewidth = 2*lorentzian_result.best_values["sigma"]

        # Does not depend on the Lorentzian, calculate separately
        self.raw_area = np.trapz(self.spectrum)
        return 

# End SplitBandData



@dataclass
class HeterodyneData(SpectrumFile):
    """
    Class for working with heterodyne data.
    Example:  `het_st80_1.CSV`

    NB: Scipy's optimize module has been shown to fit multiple peaks with less
        error than a composite model from LMFIT. For this use case, we only care
        about the measurements of the fit (e.g. FWHM, mechanical frequency, linewidth).
    """  

    # Composite Lorentzian
    raw_area: float = field(init=False)
    fit_area: float = field(init=False)

    # Main (center) peak
    main_area: float = field(init=False)
    main_mechanical_frequency: float = field(init=False)
    main_linewidth: float = field(init=False)
    
    # Peak to the left/right of main peak
    left_area: float = field(init=False)
    left_mechanical_frequency: float = field(init=False)
    left_linewidth: float = field(init=False)
    
    # Peak to the right/left of main peak
    right_area: float = field(init=False)
    right_mechanical_frequency: float = field(init=False)
    right_linewidth: float = field(init=False)
    

    def __post_init__(self):
        super().__post_init__()
        return



    def _single_peak_lorentzian(self, x, amp, cen, wid, back=0.0):
        """
        Definition of a Lorentzian with a single peak. 
        See https://docs.astropy.org/en/stable/api/astropy.modeling.functional_models.Lorentz1D.html

        Args:
        x (np.ndarray(float)):  Values where the Lorentzian is evaluated.

        amp (float):  The amplitude of the peak.

        cen (float):  The value in the domain where the peak is found.

        wid (float):  Full width at half maximum (FWHM).

        back (float, optional): A cosntant representing the background offset.
                                Defaults to 0.0

        Returns:
        (np.ndarray(float)):  Values for the Lorentzian computed over `x`
        """
        return (amp*wid**2/((x-cen)**2+wid**2))+back


    def _three_peaks_lorentzian(self, x,
                                amp1, cen1, wid1, 
                                amp2, cen2, wid2,
                                amp3, cen3, wid3):
        
        return self._single_peak_lorentzian(x, amp1, cen1, wid1) + self._single_peak_lorentzian(x, amp2, cen2, wid2) + self._single_peak_lorentzian(x, amp3, cen3, wid3)


    def _peak_selection(self):
        # Locate peaks in the spectrum by index
        peak_indices, _ = find_peaks(self.spectrum)
        # Select corresponding amplitudes of found peaks
        peak_amplitudes = self.spectrum[peak_indices]
        
        # Sort the peaks according to height; largest to smallest
        amp_idx_pairs = list(zip(peak_amplitudes, peak_indices)) 
        amp_idx_pairs.sort(key=lambda pair : pair[0], reverse=True)

        # Track the left and right side peaks
        left_pair = None
        right_pair = None

        # Main (center) peak is always the tallest
        main_pair = amp_idx_pairs[0]

        # The next tallest peak should appear on one side of the main peak
        side_a_pair = amp_idx_pairs[1]

        # The next side peak depends on where side_a peak is located
        side_b_pair = None
        # The side a peak was left of the main peak
        if side_a_pair[1] < main_pair[1]:
            left_pair = side_a_pair
            # Compare indices to find the tallest peak on the right of the main peak
            right_pair = (next(pair for pair in amp_idx_pairs[2:] if pair[1] > main_pair[1]))
        # The side a peak was right of the main peak
        else:
            right_pair = side_a_pair
            # Compare indices to find the tallest peak on the left of the main peak
            left_pair = (next(pair for pair in amp_idx_pairs[2:] if pair[1] < main_pair[1]))

        return (main_pair, left_pair, right_pair)
    


    def fit_3d_lorentzian(self):

        # Locate desired peaks
        main_pair, left_pair, right_pair = self._peak_selection()

        # Set up initial guesses from peaks
        main_amp = main_pair[0]
        main_cen = self.frequencies[main_pair[1]]

        left_amp = left_pair[0]
        left_cen = self.frequencies[left_pair[1]]

        right_amp = right_pair[0]
        right_cen = self.frequencies[right_pair[1]]
        
        # Arbitrary, seem to work well
        wid1, wid2, wid3 = (50, 25, 25)

        # Initial guess list for fitting function call
        p0 = [main_amp, main_cen, wid1, \
              left_amp, left_cen, wid2, \
              right_amp, right_cen, wid3]

        
        # Find the best fit Lorentzian
        optimal_params, _ = scipy.optimize.curve_fit(self._three_peaks_lorentzian,
                                                     self.frequencies,
                                                     self.spectrum,
                                                     p0=p0,
                                                     maxfev=5000)
        
        # Define the optimal parameters from the fitting operation
        main_params = optimal_params[0:3]
        left_params = optimal_params[3:6]
        right_params = optimal_params[6:9]

        # Compute Lorentzians for each peak using the optimal parameters
        main_lorentzian = self._single_peak_lorentzian(self.frequencies, *main_params)
        left_lorentzian = self._single_peak_lorentzian(self.frequencies, *left_params)
        right_lorentzian = self._single_peak_lorentzian(self.frequencies, *right_params)
        composite_lorentzian = self._three_peaks_lorentzian(self.frequencies, *main_params, *left_params, *right_params)

        # Set the attributes of the Heterodyne object
        # Composite Lorentzian
        self.raw_area = np.trapz(self.spectrum)
        self.fit_area = np.trapz(composite_lorentzian)

        # Main (center) peak
        self.main_area = np.trapz(main_lorentzian)
        self.main_mechanical_frequency = main_params[0]
        self.main_linewidth = main_params[2]
        
        # Peak to the left/right of main peak
        self.left_area = np.trapz(left_lorentzian)
        self.left_mechanical_frequency = left_params[0]
        self.left_linewidth = left_params[2]
        
        # Peak to the right/left of main peak
        self.right_area = np.trapz(right_lorentzian)
        self.right_mechanical_frequency = right_params[0]
        self.right_linewidth = right_params[2]

        return (main_lorentzian, left_lorentzian, right_lorentzian, composite_lorentzian)

# End HeterodyneData