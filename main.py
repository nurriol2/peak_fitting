import logging
FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
from setup import build_file_tree
from data_toolbox.preprocessing import ready_all_ucl
from data_toolbox.preprocessing import ready_all_cst

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
    ready_all_cst()


    return 

if __name__=="__main__":
    main()