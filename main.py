from setup import build_file_tree, data_loc
from data_toolbox.workflows import hetr_sideband_workflow
from data_toolbox.workflows import split_area_workflow

import pprint
def main():
    # Build a file tree for the experiment data
    build_file_tree()

    # UCL Data Demos
    # Demonstrate coefficient estimation for all parameters found in sideband data
    for c in ["area_x", "freq_x", "linewidth_x", "area_y", "freq_y", "linewidth_y"]:
        hetr_sideband_workflow.run_ucl_workflow(data_loc["ucl"], "fit_neg_sideband.dat", c)

    split_area_workflow.run_ucl_workflow(data_loc["ucl"], "areax.dat")
    split_area_workflow.run_ucl_workflow(data_loc["ucl"], "fx.dat")

    # Custom Framework Demos

    return 

if __name__=="__main__":
    main()