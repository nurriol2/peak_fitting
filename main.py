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
    # print(ucl.area_report) 
    # print(ucl.freq_report) 
    # print(ucl.line_report) 
    
    ### Custom Analysis ###
    
    ## Split Detection Data ##
    # "cha" <--> "x" and "chb" <--> "y" throughout
    cst = CustomWorkflow()
    # This runs "chb" data
    cst.target_split_detection(mode='y')
    # print(cst.area_report) 
    # print(cst.freq_report) 
    # print(cst.line_report) 
    

    cst = CustomWorkflow()
    cst.target_heterodyne(which_sideband="pos")
    print(cst.area_report) 
    print(cst.freq_report) 
    print(cst.line_report) 


if __name__=="__main__":
    main()