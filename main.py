from data_toolbox.lorentz import Lorentzian
from setup import build_file_tree
from data_toolbox.workflows.ucl_workflow import UCLWorkflow
from data_toolbox.workflows.custom_workflow import CustomWorkflow

def main():

    # # Setup the experiment data directory no matter what platform this is executed on
    build_file_tree()

    # ## Compare Split Detection Reports ##
    ucl = UCLWorkflow()
    cst = CustomWorkflow()

    # # Specify the sideband and directional mode
    SIDEBAND = "pos"
    MODE = 'y'

    # Analyze heterodyne data 
    ucl.target_heterodyne(SIDEBAND, MODE)
    cst.target_heterodyne(SIDEBAND, MODE)

    # Estimated coefficients for mechanical frequency should be close
    print(ucl.freq_report)
    print(cst.freq_report)

    # from data_toolbox.spectra import HeterodyneData
    # import matplotlib.pyplot as plt
    # from setup import HETERODYNE_RAW

    # EXAMPLE_HETR = "het_st80_83.CSV"
    # HETR_UNITS = "V^2/Hz"
    # zoom = 50

    # hetr = HeterodyneData(HETERODYNE_RAW, EXAMPLE_HETR, HETR_UNITS)
    
    # # Worked ok for positive sideband
    # # hetr.trim_spectrum_to_sideband("pos", 1_000)
    # # Fit a lorentzian
    # # lorentzian = hetr.fit_lorentzian("pos", 'y')


    # # Worked ok for negative sideband
    # hetr.trim_spectrum_to_sideband("neg", 200, -1_000)
    # # Fit a lorentzian
    # lorentzian = hetr.fit_lorentzian("neg", 'y')

    # plt.plot(hetr.frequencies, hetr.spectrum)
    # plt.plot(hetr.frequencies, lorentzian.values)
    # plt.show()
    

    return

if __name__=="__main__":
    main()