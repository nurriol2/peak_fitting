import numpy as np

def find_index_of_closest_slope(x, y, slope):
    
    # Tansform x and y into log space
    logx = np.log10(x)
    logy = np.log10(y)

    # Calculate the derivative of the curve y(x) in log space
    dlogy = np.divide(np.diff(logy), np.diff(logx))

    # Calculate the index where value of derivative is closest to desired slope
    target_index = np.abs(dlogy-slope).argmin()

    return target_index

def calculate_log_space_y_intercept(x, y, slope, target_index):
    
    # Transform x and y into log space
    logx = np.log10(x)
    logy = np.log10(y)

    # Calculate the y intercept in log space
    intercept = logy[target_index] - slope*logx[target_index]

    return intercept

def calculate_coeff_from_slope(slope, tau_star, intercept):

    # Compute coefficient in log space
    logCoeff = slope*np.log10(tau_star) + intercept

    # Undo log base 10
    coeff = 10**logCoeff

    return coeff

def calculate_coeff_with_slope_zero(intercept):
    
    # Bias instability coefficient is scaled by ~0.664
    SCALE_FACTOR = (2*np.log(2)/np.pi)**0.5

    # Computer coefficient in log space
    logCoeff = intercept - np.log10(SCALE_FACTOR)

    # Undo log base 10
    coeff = 10**logCoeff

    return coeff


def fit_random_walk_line(tau_array, allan_array):
    
    # Random walk coefficient found when tau = 1
    TAU_STAR = 1
    # Random walk appears with slope -0.5 on Allan deviation plot
    RW_SLOPE = -0.5
    # Find where Allan deviation curve has slope closest to -0.5
    rw_index = find_index_of_closest_slope(tau_array, allan_array, RW_SLOPE)
    # Calculate the intercept for the fit line
    rw_intercept = calculate_log_space_y_intercept(tau_array, allan_array, RW_SLOPE, rw_index)
    # Calculate the random walk coefficient 
    computed_coeff = calculate_coeff_from_slope(RW_SLOPE, TAU_STAR, rw_intercept)

    # Array of unscaled cluster times
    t = np.power(tau_array, 0.5)
    
    return (np.divide(computed_coeff, t), computed_coeff)

def fit_rate_random_walk_line(tau_array, allan_array):
    
    # Rate random walk coefficient found when tau = 3
    TAU_STAR = 3
    # Rate random walk appears with slope +0.5 on Allan deviation plot
    RRW_SLOPE = 0.5
    # Find where Allan deviation curve has slope closest to 0.5
    rrw_index = find_index_of_closest_slope(tau_array, allan_array, RRW_SLOPE)
    # Calculate the intercept for the fit line
    rrw_intercept = calculate_log_space_y_intercept(tau_array, allan_array, RRW_SLOPE, rrw_index)
    # Calculate the rate random walk coefficient
    computed_coeff = calculate_coeff_from_slope(RRW_SLOPE, TAU_STAR, rrw_intercept)

    # Array of unscaled cluster times
    t = np.power(np.divide(tau_array,3), 0.5)
    
    return (computed_coeff * t, computed_coeff)

def fit_bias_instability_line(tau_array, allan_array):

    # Bias instability appears with slope 0 on Allan deviation
    BI_SLOPE = 0

    # Find where the Allan deviation has slope closest to 0
    bi_index = find_index_of_closest_slope(tau_array, allan_array, BI_SLOPE)
    
    # Calculate intercept for fit line
    bi_intercept = calculate_log_space_y_intercept(tau_array, allan_array, BI_SLOPE, bi_index)

    # Calculate the bias instability coefficient
    computed_coeff = calculate_coeff_with_slope_zero(bi_intercept)

    # Horizontal line 
    t = np.ones(len(tau_array))

    return (computed_coeff * (2*np.log(2)/np.pi)**0.5 * t, computed_coeff)