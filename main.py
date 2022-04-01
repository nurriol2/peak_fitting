from setup import build_file_tree
from data_toolbox.workflows.ucl_workflow import UCLWorkflow
from data_toolbox.workflows.custom_workflow import CustomWorkflow

def main():

    # Setup the experiment data directory no matter what platform this is executed on
    build_file_tree()

    ## Compare Split Detection Reports ##
    ucl = UCLWorkflow()
    cst = CustomWorkflow()

    # Target split detection data set
    ucl.target_split_detection('x')
    cst.target_split_detection('x')

    # Target heterodyne data set
    #ucl.target_heterodyne("pos", "y")
    #cst.target_heterodyne("pos")

    print(ucl.freq_report)
    print(cst.line_report)

    return

if __name__=="__main__":
    main()