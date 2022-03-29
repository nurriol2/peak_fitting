import numpy as np

class Lorentzian:
    """
    A single peak Lorentzian.
    See https://docs.astropy.org/en/stable/api/astropy.modeling.functional_models.Lorentz1D.html

    Attrs:
    x (np.ndarray):  Points where the Lorentzian is evaluated.
    
    amp (float): The amplitude of the peak.

    cen (float):  The x-coodrinate of the Lorentzian peak.

    wid (float):  Half of the full width at half maximum (0.5*FWHM).

    back (float, optional): A cosntant representing the background offset.
                            Defaults to 0.0

    values (np.array): Values of the Lorentzian over x. Use these for plotting.
    """

    def __init__(self, x, amp, cen, wid, back):
        self.x = x
        self.amp = amp
        self.cen = cen
        self.wid = wid
        self.back = back
        self.values = self._single_peak_lorentzian()
        return 


    def _single_peak_lorentzian(self):
        """
        Calculate values of a single peak Lorentzian according to object attributes.

        Returns:
        (np.ndarray(float)):  Values for the Lorentzian computed over `x`
        """
        return (self.amp*self.wid**2/((self.x-self.cen)**2+self.wid**2))+self.back


    def area_under_curve(self):
        """
        Calculate the area under the Lorentzian.

        Returns:
        (float):  Area under the Lorentzian. 
        """
        return np.trapz(self.values)
    

    def mechanical_frequency(self):
        """
        Determine the amplitude of the peak.

        Returns:
        (float:  Amplitude of the peak.
        """
        return max(self.values)
    

    def linewidth(self):
        """
        Calculate the FWHM.

        Returns:
        (float):  The FWHM of the Lorentzian.
        """
        return 2*self.wid


    def all_values(self):
        """
        Create a dictionary of attributes, subscriptable by name.

        Returns:
        (dict):  Keys are fit_area, mechanical_frequency, and linewidth.
        """
        return {"fit_area":self.area_under_curve(),
                "mechanical_frequency":self.mechanical_frequency(),
                "linewidth":self.linewidth()}

# End Lorentzian