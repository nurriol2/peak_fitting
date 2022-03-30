# Workflow used:  "UCL"
# Data source used:  "areax.dat"
# Parameter analyzed:  "Area under Lorentzian fit"
# Coefficient Estimated Values:
#       Random Walk: NNN.nnn
#       Bias Instability: NNN.nnn
#       Rate Random Walk:  NNN.nnn

# Workflow used:  "Custom"
# Data source used:  "split_detection/cha_st80_N.CSV"
# Parameter analyzed:  "Area under Lorentzian fit"
# Coefficient Estimated Values:
#       Random Walk: NNN.nnn
#       Bias Instability: NNN.nnn
#       Rate Random Walk:  NNN.nnn

from dataclasses import dataclass

@dataclass
class Report:

    workflow_used: str
    data_source: str
    parameter: str
    coefficients: dict

    def __str__(self):
        printable_str = f"""
                        Workflow used:  {self.workflow_used}
                        Data source:  {self.data_source}
                        Parameter analyzed:  {self.parameter}
                        Coefficient Estimated Values:
                              Random Walk: {self.coefficients["Random Walk"]}
                              Bias Instability: {self.coefficients["Bias Instability"]}
                              Rate Random Walk:  {self.coefficients["Rate Random Walk"]}
                        """
        return printable_str