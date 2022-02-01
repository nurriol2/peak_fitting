import pandas as pd
from classes import SplitBandData, HeterodyneData

def extract_single_peak(directory, pattern):
    raw_area = []
    fit_area = []
    mechanical_frequency = []
    linewidth = []

    for i in range(1,125):
        data = SplitBandData(directory, pattern, "m^2/Hz")
        data.fit_1d_lorentzian()
        raw_area.append(data.raw_area)
        fit_area.append(data.fit_area)
        mechanical_frequency.append(data.mechanical_frequency)
        linewidth.append(data.linewidth)
    
    values = {"raw_area":raw_area,
                "fit_area":fit_area,
                "mechanical_frequency":mechanical_frequency,
                "linewidth":linewidth}
    return values 

def main():
    CHANNEL_A_PATTERN = "cha_st80_*.CSV"
    CHANNEL_A_DIRECTORY = "/content/split_detection/"

    CHANNEL_B_PATTERN = "chb_st80_*.CSV"
    CHANNEL_B_DIRECTORY = "/content/split_detection/"
    
    HETERODYNE_PATTERN = "het_st80_*.CSV"
    HETERODYNE_DIRECTORY = "/content/heterodyne/"
    return 

if __name__=="__main__":
    main()