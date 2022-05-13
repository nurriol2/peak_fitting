import logging
FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
from setup import build_file_tree
from data_toolbox.preprocessing import find_split_detection_spectra, ready_all_ucl
from data_toolbox.preprocessing import preprocess_cst_split_detection as cst_split
from data_toolbox.preprocessing import one_split_detection_cycle

def report_printer():
    from data_toolbox.workflows.ucl_workflow import UCLWorkflow
    from data_toolbox.workflows.custom_workflow import CustomWorkflow


    ## Compare Split Detection Reports ##
    ucl = UCLWorkflow()
    cst = CustomWorkflow()

    # Specify the sideband and directional mode
    SIDEBAND = "neg"
    MODE = 'x'

    # Analyze heterodyne data
    ucl.target_heterodyne(SIDEBAND, MODE)
    cst.target_heterodyne(SIDEBAND, MODE)

    # Estimated coefficients for mechanical frequency should be close
    print(ucl.freq_report)
    print(cst.freq_report)

    return

def main():
    build_file_tree()
    ready_all_ucl()
    file_list = find_split_detection_spectra('x')
    logging.debug(f"Num found:  {len(file_list)}")
    logging.debug(f"List of files:  {file_list[:3]}")

    p = file_list[0]
    logging.debug(f"Path to a file {p}")
    l = one_split_detection_cycle(p)
    logging.debug(f"Lorentzian Object:  {l}")
    return 

if __name__=="__main__":
    main()