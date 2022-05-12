# ├── raw_data
# │   ├── heterodyne
# │   │   ├── het_st80_1
# |   |   ├── ...
# │   ├── split_detection
# │   |   ├── cha_st80_1
# │   |   ├── ...
# │   |   ├── chb_st80_1
# │   |   ├── ...
# │   ├── raw_ucl_fits
# │   |   ├── areax.dat
# │   |   ├── areay.dat
# │   |   ├── fit_neg_sideband.dat
# │   |   ├── fit_pos_sideband.dat
# │   |   ├── fx.dat
# │   |   ├── fy.dat
# │   ├── heterodyne.zip
# │   ├── split_detection.zip
# ├── clean_data # Name convention:  source_mode_sideband.CSV
# │   ├── heterodyne
# │   │   ├── cst_x_negative.CSV
# │   │   ├── cst_x_positive.CSV
# │   │   ├── cst_y_negative.CSV
# │   │   ├── cst_y_positive.CSV
# │   │   ├── ucl_x_negative.CSV
# │   │   ├── ucl_x_positive.CSV
# │   │   ├── ucl_y_negative.CSV
# │   │   ├── ucl_y_positive.CSV
# │   ├── split_detection
# │   │   ├── cst_x_none.CSV
# │   │   ├── cst_y_none.CSV
# │   │   ├── ucl_x_none.CSV
# │   │   ├── ucl_y_none.CSV

import os
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logging.disable(logging.CRITICAL)

# Full path to the location of this file
PREFIX = os.path.join(os.getcwd(), "experiment_data/")

# Top level directory for all raw data
RAW_DATA_DIR = os.path.join(PREFIX, "raw_data/")

# Top level directory for files that have been processed
CLEAN_DATA_DIR = os.path.join(PREFIX, "clean_data/")


def _add_child_dirs(parent, children):

    """
    Create sub directories as children of a parent directory.

    Args:
    parent (string):  Parent directory name.
    children (list(string)):  List of subdirectory names.
    """

    for child in children:
        # Apply basic formatting for the subdirectory name
        fmt_name = child.lower().replace(' ', "_")
        dir_path = os.path.join(parent, fmt_name)
        
        # Check directory path in the terminal
        try:
            os.makedirs(dir_path)
            logging.debug(f"Created {dir_path}")
        except FileExistsError:
            logging.debug(f"Skipping {dir_path}...")

    return 


def _add_files(parent, filenames):

    """
    Exclusively create a file under the parent directory
    for each file in a list.

    parent (string):  Parent directory.
    filename (string):  Name of the file to be created. 
    """

    # Column names
    header = "time_step,area_under_curve,mechanical_frequency,linewidth"

    for filename in filenames:
        # Path to the desired file
        fullpath = os.path.join(parent, filename)

        # Attempt to create the file
        # TODO:  Could this be better with a context manager?
        try:
            f = open(fullpath, 'w')
            f.write(header)
            f.close()
        except FileExistsError:
            logging.debug(f"{fullpath} already exists.")

    return  


def build_file_tree():

    """
    Create a file tree for the pre- and post-processed experiment data.
    Initialize template files for post-processed data.
    """

    # Create directory for UCL fits
    _add_child_dirs(RAW_DATA_DIR, ["raw_ucl_fits"])
    

    # Create child directories to CLEAN_DATA_DIR
    clean_subdirs = ["split_detection", "heterodyne"]
    _add_child_dirs(CLEAN_DATA_DIR, clean_subdirs)



    # Cleaned heterodyne files
    hetr_template_files = ["cst_x_positive.CSV", "cst_x_negative.CSV", 
                            "ucl_x_positive.CSV", "ucl_x_negative.CSV",
                            "cst_y_positive.CSV", "cst_y_negative.CSV", 
                            "ucl_y_positive.CSV", "ucl_y_negative.CSV"]
    # Path to clean heterodyne directory
    clean_heterodyne_path = os.path.join(CLEAN_DATA_DIR, "heterodyne/")
    # Add files to clean heterodyne directory
    _add_files(clean_heterodyne_path, hetr_template_files)


    # Cleaned split detection files
    split_detection_template_files = ["cst_x_none.CSV", "cst_y_none.CSV", 
                                        "ucl_x_none.CSV", "ucl_y_none.CSV"]
    # Path to clean split detection directory
    clean_split_detection_path = os.path.join(CLEAN_DATA_DIR, "split_detection/")
    # Add files to clean split detection directory
    _add_files(clean_split_detection_path, split_detection_template_files)

    return 