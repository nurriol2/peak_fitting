import pandas as pd
import numpy as np 
import data_toolbox.constants as constants
import data_toolbox.spectra as spectra

### General Helper Functions ###

abbreviate_sideband = lambda sideband: sideband.lower().strip()[0:3]

def load_raw_sideband(sideband):
    """
    Load a `fit_{sideband}_sideband.dat` file into memory as a dataframe.
    
    Assign the column labels according to the ReadMe.txt. 
    Since the ReadMe does not specify the 7th column label, the column
    label is assigned by this function as `error`. 
    
    Args:
        sideband (str, optional):  Heterodyne sideband identifier. 

    Returns:
        (pandas.DataFrame):  A `fit_{sideband}_sideband.dat` file as a dataframe.
    """

    ### Point to the file ###
    # Directory of all raw UCL data
    ucl_fits_path = constants.RAW_DATA_DIRECTORY.joinpath("raw_ucl_fits")
    # Format the filename
    raw_filename_templ = f"fit_{abbreviate_sideband(sideband)}_sideband.dat"
    # Full path to the raw data
    target = ucl_fits_path.joinpath(raw_filename_templ)
    
    ### Format the dataframe ###
    col_names = ["Area_x", "f_x", "linewidth_x", "Area_y", "f_y", "linewidth_y", "error"]
    raw_df = pd.read_csv(target, names=col_names, sep="\t")

    return raw_df

def clean_path(source, mode, sideband=None):

    """
    Create path to a target file in the `clean_data` subdirectory

    Args:
        source (str):  Data source identifier for the clean filename template.
                       Must be either "ucl" or "cst"
        
        mode (str):  Directional mode identifier for the clean filename template.
                     Must be either 'x' or 'y'

        sideband (str, optional):  Sideband identifier for the clean filename template. 
                                   If "positive" or "negative", target is assumed a child of `heterodyne/`
                                   If None, target is assumed to be a child of `split_detection/`
                                   Defaults to None.
    
    Returns:
        (pathlib.ConcretePath):  Object representing path to the target using the OS flavor of path formatting.
    """


    # Assume the filepath is to file in the heterodyne subdirectory
    subdirectory = "heterodyne"

    # A heterodyne sideband is not provided
    # Filepath must be to file in the split detection subdirectory
    if sideband is None:
        # Split detection files always have "none" as their sideband id
        sideband = "none"
        subdirectory = "split_detection"

    # Format the filename
    filename = f"{source}_{mode}_{sideband}.CSV"

    # Path to the desired file
    filepath = constants.CLEAN_DATA_DIRECTORY.joinpath(subdirectory, filename)

    return filepath

def ready_all_ucl():
    
    """
    Convenience function to clean the data from raw UCL fits. 

    Preproccess raw split detection data for each directional mode.
    Preproccess raw heterodyne data for each directional mode and sideband.
    Processed files should be populated under `experiment_data/clean_data/...`
    """

    preprocess_ucl_split_detection('x')
    preprocess_ucl_heterodyne('x', "positive")
    preprocess_ucl_heterodyne('x', "negative")
    preprocess_ucl_split_detection('y')
    preprocess_ucl_heterodyne('y', "positive")
    preprocess_ucl_heterodyne('y', "negative")

    return 



### Data Source Specific Preproccessing Functions ### 
def preprocess_ucl_split_detection(mode):

    """
    Preprocess raw split detection data into a CSV for the specified mode.

    Args:
        mode (str):  Directional mode identifier for the clean filename template.
                     Must be either 'x' or 'y'
    """

    # Directory of all raw UCL data
    ucl_fits_path = constants.RAW_DATA_DIRECTORY.joinpath("raw_ucl_fits")
    

    ### Load time series data for each column into memory ###
    area_under_curve = np.loadtxt(ucl_fits_path.joinpath(f"area{mode}.dat"))

    mechanical_frequency = np.loadtxt(ucl_fits_path.joinpath(f"f{mode}.dat"))

    # Linewidth data was not fit by UCL. Placeholder signal is used instead.
    # Placeholder has the same shape as area under curve Series.
    aoc_shape = area_under_curve.shape
    linewidth = np.full(shape=aoc_shape, fill_value=-1*np.inf)
    
    time_step = np.arange(0, len(area_under_curve)) * constants.SPLIT_DETECTION_SAMLPING_STEP_SIZE


    # Read in the clean file as a data frame
    target = clean_path(source="ucl", mode=mode, sideband=None)

    df = pd.read_csv(target)
    
    # Populate the columns 
    df["area_under_curve"] = area_under_curve
    df["mechanical_frequency"] = mechanical_frequency
    df["linewidth"] = linewidth
    df["time_step"] = time_step

    # Write the populated data frame to the CSV
    df.to_csv(target, index_label="index")

    return 

def preprocess_ucl_heterodyne(mode, sideband):
    """
    Preprocess raw heterodyne data into a CSV for the specified directional mode and sideband.

    Args:
        mode (str):  Directional mode identifier for the clean filename template.
                     Must be either 'x' or 'y'

        sideband (str):  Sideband identifier for the clean filename template. 
    """

    ### Locate raw data file ###
    # Load the corresponding heterodyne fit into memory as a dataframe
    df = load_raw_sideband(sideband=sideband)
    # Filter the columns by the directional mode
    matched_df = df.filter(regex=f"\w+{mode}")

    ### Rename the matched column names to the standard set of names ###
    current_names = list(matched_df.columns)
    standard_names = ["area_under_curve" ,"mechanical_frequency" ,"linewidth"]
    name_map = {curr:std for curr,std in list(zip(current_names, standard_names))}
    matched_df = matched_df.rename(columns=name_map)


    # Create data for time step column
    time_step = np.arange(0, len(matched_df)) * constants.SPLIT_DETECTION_SAMLPING_STEP_SIZE
    # Insert the time step column into the matching dataframe
    matched_df.insert(0, "time_step", time_step)

    ### Write dataframe to file ###
    target = clean_path(source="ucl", mode=mode, sideband=sideband)
    matched_df.to_csv(target, index_label="index")
    
    return 

def find_split_detection_spectra(mode):
    """
    Search `experiment_data/raw_data/split_detection` for all split detection CSV files
    for a specific directional mode.

    Args:
        mode (str):  Directional mode identifier for split detection data.
                     Must be either 'x' or 'y'

    Returns:
        (list(pathlib.Path)):  A list of split detection data files sorted by file number.
    """

    # Path to directory of raw split detection data
    split_det_dir = constants.RAW_DATA_DIRECTORY.joinpath("split_detection")

    # Filename prefix depends on the directional mode 
    prefix = {
        'x':"cha",
        'y':"chb"
    }

    # Formatted filename depending on the specified mode
    pattern = f"{prefix[mode]}_st80_*.CSV"
    
    # Match all split detection files within the raw directory for the given mode
    matching_files = list(split_det_dir.rglob(pattern=pattern))

    # The final Path component contains the file number
    # The file number is always the 2th element after splitting by '_' (with this naming scheme)
    # Cast the numeric part as int to sort by increasing order
    key = lambda p: int(p.stem.split('_')[2])
    # Sort by increasing file number
    matching_files.sort(key=key, reverse=False)
    
    return matching_files

def one_split_detection_cycle(spectrum_path):

    """
    Fit a Lorentzian to a single raw split detection data file.
    
    Args:
        spectrum_path (pathlib.Path):  Path to a single raw split detection data file.

    Returns:
        (Lorentzian): An object representing the best fit single peak Lorentzian 
                      to the split detection data.
                      Lorentzian objects have methods defined for computing the
                      area under the curve, mechanical frequency, and linewidth.
    """

    # Raw split detection data directory
    directory = str(spectrum_path.parent)
    # Example:  ch*_st80_###.CSV; File suffix is required
    pattern = str(spectrum_path.name)

    # Create a split detection file object
    split_det_obj = spectra.SplitDetectionData(directory=directory, pattern=pattern, units=constants.SPLIT_DETECTION_UNITS)

    # Fit a lorentzian to the split detection object
    lorentz = split_det_obj.init_lorentzian()

    return lorentz

def preprocess_cst_split_detection(mode):

    """
    Preprocess raw split detection data into a CSV for the specified mode.

    Args:
        mode (str):  Directional mode identifier for the clean filename template.
                     Must be either 'x' or 'y'
    """

    # List of Paths to all raw split detection files with specified mode
    split_detection_paths = find_split_detection_spectra(mode=mode)

    # Container for array of time series (per feature)
    feature_arrays = {
        "time_step":None,
        "area_under_curve":[],
        "mechanical_frequency":[],
        "linewidth":[]
    }

    # Iterate over the file Paths
    for spectrum_path in split_detection_paths:
        # Fit a Lorentzian curve to a single split detection spectrum
        current_lorentz = one_split_detection_cycle(spectrum_path=spectrum_path)
        ### Measure features of the best fit Lorentzian ###
        ### Add measurements to the corresponding array of `feature_arrays`
        feature_arrays["area_under_curve"].append(current_lorentz.area_under_curve())
        feature_arrays["mechanical_frequency"].append(current_lorentz.mechanical_frequency())
        feature_arrays["linewidth"].append(current_lorentz.linewidth())

    # Create the time step array independent of the Lorentzian features
    feature_arrays["time_step"] = np.arange(0, len(feature_arrays["area_under_curve"])) * constants.SPLIT_DETECTION_SAMLPING_STEP_SIZE

    ### Write the collected feature measurements to a frame ###
    target = clean_path(source="cst", mode=mode)
    df = pd.read_csv(target)

    # Keys of the features are the same as column labels
    for key in feature_arrays.keys():
        df[key] = feature_arrays[key]

    # Actual write func call
    df.to_csv(target, index_label="index")

    return 

def find_heterodyne_spectra():
    """
    Search `experiment_data/raw_data/heterodyne` for all heterodyne CSV files.

    Takes no arguments because, for a single file, different mode and sideband
    identifiers will access the same file.
    For example, loading (x, negative) and (y, positive) portions of het_st80_32.CSV
    both require het_st80_32.CSV.

    Returns:
        (list(pathlib.Path)):  A list of split detection data files sorted by file number.
    """

    # Path to directory of raw heterodyne data
    hetr_dir = constants.RAW_DATA_DIRECTORY.joinpath("heterodyne")

    # Filename pattern for heterodyne spectra
    pattern = "het_st80_*.CSV"

    # Match all heterodyne files within the raw heterodyne directory
    matching_files = list(hetr_dir.rglob(pattern=pattern))

    # The final Path component contains the file number
    # The file number is always the 2th element after splitting by '_' (with this naming scheme)
    # Cast the numeric part as int to sort by increasing order
    key = lambda p: int(p.stem.split('_')[2])
    # Sort by increasing file number
    matching_files.sort(key=key, reverse=False)

    return matching_files

def one_heterodyne_cycle(spectrum_path, mode, sideband):

    """
    Fit a Lorentzian to a single raw heterodyne data file.

    The negative sideband is always the region LEFT of the center peak.
        The peak at the lower frequency in this region is the Y mode.
        The peak at the higher frequency in this region is the X mode.

    The positive sideband is always the region RIGHT of the center peak.
        The peak at the lower frequency in this region is the X mode.
        The peak at the higher frequency in this region is the Y mode.

    Args:
        spectrum_path (list(pathlib.Path)): Path to a single raw heterodyne data file.

        mode (str):  Directional mode identifier.
                     Must be either 'x' or 'y'

        sideband (str):  Sideband identifier. 
                         Must be either "positive" or "negative".

    Returns:
        (Lorentzian): An object representing the best fit single peak Lorentzian 
                      to the split detection data.
                      Lorentzian objects have methods defined for computing the
                      area under the curve, mechanical frequency, and linewidth.


    """
    
    # (Workaround) Format sideband identifier to use trimming functions
    # TODO:  Change spectra module to use "positive" and "negative" 
    which_sideband = {
        "positive":"pos",
        "negative":"neg"
    }

    # Raw heterodyne data directory
    directory = str(spectrum_path.parent)
    # Example:  het_st80_###.CSV; File suffix is required
    pattern = str(spectrum_path.name)

    # Create a heterodyne file object
    hetr_obj = spectra.HeterodyneData(directory=directory, pattern=pattern, units=constants.HETERODYNE_UNITS)

    # Fitting a Lorentzian works best if the data is trimmed first
    # Trim according to the sideband of interest
    if sideband == "positive":
        hetr_obj.trim_spectrum_to_sideband(which_sideband=which_sideband[sideband], tune_start=constants.POS_START_ADJ)
    if sideband == "negative":
        hetr_obj.trim_spectrum_to_sideband(which_sideband=which_sideband[sideband], tune_start=constants.NEG_START_ADJ, tune_end=constants.NEG_END_ADJ)
    
    # Fit a Lorentzian according to the specified peak
    lorentz = hetr_obj.fit_lorentzian(which_sideband=which_sideband[sideband], mode=mode)

    return lorentz

def preprocess_cst_heterodyne(mode, sideband):
    

    # List of Paths to all raw heterodyne detection files
    heterodyne_paths = find_heterodyne_spectra()

    # Container for array of time series (per feature)
    feature_arrays = {
        "time_step":None,
        "area_under_curve":[],
        "mechanical_frequency":[],
        "linewidth":[]
    }

    # Iterate over the file Paths
    for spectrum_path in heterodyne_paths:
        # Fit a Lorentzian curve to a single heterodyne spectrum
        current_lorentz = one_heterodyne_cycle(spectrum_path=spectrum_path, mode=mode, sideband=sideband)
        ### Measure features of the best fit Lorentzian ###
        ### Add measurements to the corresponding array of `feature_arrays`
        feature_arrays["area_under_curve"].append(current_lorentz.area_under_curve())
        feature_arrays["mechanical_frequency"].append(current_lorentz.mechanical_frequency())
        feature_arrays["linewidth"].append(current_lorentz.linewidth())

    # Create the time step array independent of the Lorentzian features
    feature_arrays["time_step"] = np.arange(0, len(feature_arrays["area_under_curve"])) * constants.HETERODYNE_SAMPLING_STEP_SIZE

    ### Write the collected feature measurements to a frame ###
    target = clean_path(source="cst", mode=mode, sideband=sideband)
    df = pd.read_csv(target)

    # Keys of the features are the same as column labels
    for key in feature_arrays.keys():
        df[key] = feature_arrays[key]

    # Actual write func call
    df.to_csv(target, index_label="index")

    return

def ready_all_cst():

    """
    Convenience function to clean the data from raw spectra. 
    Uses custom (cst) framework. 

    Preproccess raw split detection data for each directional mode.
    Preproccess raw heterodyne data for each directional mode and sideband.
    Processed files should be populated under `experiment_data/clean_data/...`
    """
    
    preprocess_cst_split_detection('x')
    preprocess_cst_split_detection('y')
    preprocess_cst_heterodyne('x', "positive")
    preprocess_cst_heterodyne('x', "negative")
    preprocess_cst_heterodyne('y', "positive")
    preprocess_cst_heterodyne('y', "negative")

    return 