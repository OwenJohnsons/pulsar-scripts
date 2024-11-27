import numpy as np
import argparse
from astropy.time import Time

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

def main(): 
    argparser = argparse.ArgumentParser(description="Calculate the z parameter for J0523.")
    # argparser.add_argument("f_spin", type=float, help="The spin frequency of the pulsar (Hz).", default=1000)
    
    # Positional arguments
    argparser.add_argument("tobs", type=float, help="Length of observation (seconds).")
    argparser.add_argument("tstart", type=str, help="Time of observation start (YYYY-MM-DDTHH:MM:SS).")

    args = argparser.parse_args()
    tstart = args.tstart   
    T_obs = args.tobs

    mjd_asc = 2456577.64636 - 2400000.5
    tstart_mjd = Time(tstart, format='isot', scale='utc').mjd

    k2 =  190300 # semi-amplitude of radial velocity in m/s
    P_orb = 59454.432  # Orbital period in seconds (~16.67 hours)
    q = 0.61  # Mass ratio of the system
    t = 1800  # Example current time in seconds (e.g., 30 minutes into the observation)
    t_asc = 0  # Time of ascending node 

    mjd_dif_sec = (tstart_mjd - mjd_asc) * 86400
    phase = (mjd_dif_sec / P_orb) - int(mjd_dif_sec / P_orb)
    
    # seconds since ascending node
    t = phase * P_orb

    z = calculate_z(1000, k2, P_orb, q, t, t_asc, T_obs)
    print(z)

    
if __name__ == "__main__":
    main()