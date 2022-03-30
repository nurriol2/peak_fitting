from setup import build_file_tree
from data_toolbox.workflows.ucl_workflow import UCLWorkflow
from data_toolbox.workflows.custom_workflow import CustomWorkflow

def main():

    # Setup the experiment data directory no matter what platform this is executed on
    build_file_tree()

    ### UCL Analysis ###
    
    ## Split Detection Data ##
    # Define a workflow object
    ucl = UCLWorkflow()
    # Target x mode of the split detection data set
    ucl.target_split_detection(mode='x')
    # View the area report
    #print(ucl.area_report)
    # View the frequency report
    #print(ucl.freq_report)

    ## Heterodyne Data ##
    # A new workflow object
    ucl = UCLWorkflow()
    # Target the negative sideband of the heterodyne data set
    ucl.target_heterodyne(which_sideband="neg", mode='x')
    # View the reports
    #print(ucl.area_report) 
    #print(ucl.freq_report) 
    #print(ucl.line_report) 
    
    ### Custom Analysis ###
    
    ## Split Detection Data ##
    # "cha" <--> "x" and "chb" <--> "y" throughout
    cst = CustomWorkflow()
    # This runs "cha" data
    cst.target_split_detection(mode='y')
    print(cst.area_report) 
    print(cst.freq_report) 
    print(cst.line_report) 
    
"""

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