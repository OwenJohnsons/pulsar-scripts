import numpy as np

def calculate_z(f_spin, k2, P_orb, q, t, t_asc, T_obs):
    """
    Calculate the z parameter using equations 2.9, 2.10, and 2.11.
    
    Parameters:
    f_spin (float): The spin frequency of the pulsar (Hz).
    k2 (float): The semi-amplitude of the companion's radial velocity (m/s).
    P_orb (float): The orbital period (seconds).
    q (float): The mass ratio of the system.
    t (float): Current time (seconds).
    t_asc (float): Time of ascending node (seconds).
    T_obs (float): Length of observation (seconds).
    
    Returns:
    float: The calculated z value.
    """
    c = 299792458 # Speed of light (m/s)
    
    a_sin_i = (k2 * P_orb) / (2 * np.pi * q)
    
    f_dot = f_spin * (4 * np.pi**2 * a_sin_i) / (c * P_orb**2) * np.sin(2 * np.pi * (t - t_asc) / P_orb)
    
    z = f_dot * T_obs**2
    
    return z