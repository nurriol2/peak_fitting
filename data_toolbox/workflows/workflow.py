from data_toolbox.allan_func.allan import overlapping_allan_deviation as oadev
from data_toolbox.allan_func.coefficient_fitting import fit_bias_instability_line
from data_toolbox.allan_func.coefficient_fitting import fit_rate_random_walk_line
from data_toolbox.allan_func.coefficient_fitting import fit_random_walk_line



class Workflow:
    """
    Base class for executing Allan deviation noise coefficient analyses. 
    """


    def __init__(self):
        self.area_report = None
        self.freq_report = None
        self.line_report = None
        return 


    # Setters for updating individual Reports
    def _set_area_report(self, report):
        self.area_report = report
        return 
    
    def _set_freq_report(self, report):
        self.freq_report = report
        return 

    def _set_line_report(self, report):
        self.line_report = report
        return 
        

    def _run_workflow(self, signal, sampling_rate):
        """
        Method to automate the following procedure:
        1. Compute the Allan deviation
        2. Compute noise coefficients from Allan deviation
        3. Return noise coefficients

        Args:
            signal (numpy.ndarray): The data analyzed with the Allan deviation.
            sampling_rate (float): The sampling rate `signal` was collected in Hertz.

        Returns:
            dict: Keys are the names of noise sources. Values are the computed coefficients.
        """
        # Compute the Allan deviation
        tau, sigma = oadev(signal, sampling_rate)

        # Compute the error coefficients
        # The single coefficient value is the 1th argument of the returned list
        bias_instability_coeff = fit_bias_instability_line(tau, sigma)[1]
        rate_random_walk_coeff = fit_rate_random_walk_line(tau, sigma)[1]
        random_walk_coeff = fit_random_walk_line(tau, sigma)[1]
        
        # Make coeff values selectable by name
        coeff_dict = {
            "Random Walk": random_walk_coeff,
            "Bias Instability": bias_instability_coeff,
            "Rate Random Walk": rate_random_walk_coeff
        }

        return coeff_dict