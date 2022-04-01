from dataclasses import dataclass

@dataclass
class Report:
    """
    Class for neatly reporting the results of a `Workflow`.
    """

    workflow_used: str
    data_source: str
    feature: str
    coefficients: dict

    def __str__(self):
        printable_str = f"""
                        Workflow used:  {self.workflow_used}
                        Data source:  {self.data_source}
                        Feature analyzed:  {self.feature}
                        Coefficient Estimated Values:
                              Random Walk: {self.coefficients["Random Walk"]}
                              Bias Instability: {self.coefficients["Bias Instability"]}
                              Rate Random Walk:  {self.coefficients["Rate Random Walk"]}
                        """
        return printable_str