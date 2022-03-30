from setup import build_file_tree
from data_toolbox.workflows.ucl_workflow import UCLWorkflow
#from data_toolbox.workflows.custom_workflow import CustomWorkflow

def main():

    # Setup the experiment data directory no matter what platform this is executed on
    build_file_tree()

    ### UCL Analysis ###
    ucl = UCLWorkflow()
    ## Split Detection Data ##
    ucl.split_detection(mode='x')
    ucl_split_areax = ucl.area_report
    print(ucl_split_areax)
    
"""
    ucl_split_x.freq_report()
    
    ucl_split_y = UCLWorkflow.split_detection(mode="y")
    ucl_split_y.area_report()
    ucl_split_y.freq_report()


    ## Heterodyne Data ##
    # Run negative sideband data through workflow
    ucl_neg = UCLWorkflow.hetr_sideband(which_sideband="negative")
    # Query the workflow for each paremeter
    ucl_neg.area_report()
    ucl_neg.freq_report()
    ucl_neg.line_report()

    # Run positive sideband data through workflow
    ucl_pos = UCLWorkflow.hetr_sideband(which_sideband="positive")
    # Call the report to generate
    ucl_pos.area_report()
    ucl_pos.freq_report()
    ucl_pos.line_report()   

    ### Custom Analysis ###
    
    ## Split Detection Data ##
    # "cha" <--> "x" and "chb" <--> "y" throughout
    
    # This runs the "cha" data
    cst_split_x = CustomWorkflow.split_detection(mode="x")
    cst_split_x.area_report()
    cst_split_x.freq_report()
    cst_split_x.line_report()

    # Whereas, this runs the "chb" data
    cst_split_y = CustomWorkflow.split_detection(mode="y")
    cst_split_y.area_report()
    cst_split_y.freq_report()
    cst_split_y.line_report()

    ## Heterodyne Data ##
    # Positive and negative sideband data both come from the same `het_st80_.CSV` files

    # For positive, you have to `Lorentzian.fit_right_peak()`
    cst_pos = CustomWorkflow.hetr_sideband(which_sideband="positive")
    cst_pos.area_report()
    cst_pos.freq_report()
    cst_pos.line_report() 

    # For negative, you do `Lorentzian.fit_left_peak()`
    cst_neg = CustomWorkflow.hetr_sideband(which_sideband="negative")
    cst_neg.area_report()
    cst_neg.freq_report()
    cst_neg.line_report() 


    return 
"""

if __name__=="__main__":
    main()