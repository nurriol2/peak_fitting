import numpy as np
from math import log2, log10, floor, pow

def overlapping_allan_deviation(omega, Fs, maxNumM=100):
    """Calculate the overlapping Allan deviation.
    Preferred Allan deviation variant for large datasets.
    Args:
        omega (numpy array):Instantaneous output rate (or angle) measured by the IMU.
        Fs (int): Sampling frequency in Hertz (Hz).
        maxNumM (int, optional): The number of discrete time clusters. Defaults to 100.
    Returns:
        (taus, oadev) (tuple): Tuple of values.
            taus (numpy array): Array of discrete time clusters (x-values of Allan Deviation plot).
            oadev (numpy array): Array of overlapping Allan deviation estimations (y-values of Allan Deviation plot).
    """

    #sampling period in seconds
    t0 = 1/Fs

    #integrate to find angles (or rate) measured by the imu
    theta = np.cumsum(omega, 0)*t0

    #number of rows in theta vector
    L = theta.shape[0]

    #the total number of cluster times
    maxM = pow(2, floor(log2(L/2)))

    #array of all m values
    m = np.logspace(log10(1), log10(maxM), maxNumM)
    #small differences in m are unimportant
    m = np.ceil(m)
    #remove any duplicate values of m
    m = np.unique(m)
    #to use m as an index, it must be an integer
    m_ints = m.copy().astype("int32")

    #array of averaging times (x-axis values of OADEV plot)
    tau = m*t0

    #column vector of overlapping allan variance estimations (y-values of OADEV plot, but squared)
    avar = np.zeros((len(m), 1))
    
    for i in range(0, len(m)):
        #iterate over the cluster times
        mi = m_ints[i]
        #calculate the difference between adjacent cluster averages
        arg = theta[int(2*mi):L] - np.multiply(2, theta[mi:int(L-mi)]) + theta[0:int(L-2*mi)]
        #square the result
        arg_squared = np.power(arg, 2)
        #save the result in an array
        avar[i] = np.sum(arg_squared, 0)

    #calculate the coefficient of the finite sum
    denominator = np.multiply(np.multiply(2, np.power(tau, 2.0)), (L-np.multiply(2, m))).reshape(-1, 1)

    #calculate the final allan variance
    avar = avar/denominator

    #the allan deviation is the square root of the allan variance
    adev = np.sqrt(avar)

    # Reshape returned arrays to be row vectors
    tau = tau.reshape(-1,)
    adev = adev.reshape(-1,)
    
    return (tau, adev)