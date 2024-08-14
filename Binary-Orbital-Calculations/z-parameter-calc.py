#%% 
import numpy as np 

def asini(P, k2, q):
    """
    Calculate the semi-major axis of the orbit of a binary star system.

    Parameters
    ----------
    P : float
        The period of the orbit in seconds.
    k : float
        The radial velocity semi-amplitude in m/s.
    q : float
        The mass ratio of the system.

    Returns
    -------
    asini : float
    """
    return (k2*P)/(2*np.pi*q)

def spin_down(P, fspin, asini, t0, tasc):
    """
    Calculate the spin-down rate of a pulsar.

    Parameters
    ----------
    P : float
        The period of the pulsar in seconds.
    fspin : float
        The spin frequency of the pulsar in Hz.
    asini : float
        The semi-major axis of the orbit in light-seconds.
    t0 : float
        The time of periastron passage in MJD.
    tasc : float
        The time of ascending node in MJD.

    Returns
    -------
    spin_down : float
    """
    c = 299792458 # m/s
    parta = asini / c
    partb = 4*np.pi**2 / P**2
    partc = np.sin((2*np.pi * (t0 - tasc))/P)
    return parta * partb * partc * fspin 

def z_param(spin_down, Tobs): 
    """
    Calculate the z-parameter of a pulsar.

    Parameters
    ----------
    spin_down : float
        The spin-down rate of the pulsar in Hz/s.
    Tobs : float
        The observation time in seconds.

    Returns
    -------
    z : float
    """
    z = spin_down * Tobs**2 
    return z

c = 299792458 # m/s
fspin = np.linspace(100, 1000, 1000) # Hz, range of spin frequencies for known MSPs 

# J0523 calculations
P_523 = 0.068813*24*60*60 # Period in seconds 
k2_523 = 190.3*1000
q_523 = 0.61
asini_523 = asini(P_523, k2_523, q_523)
print("asini_523/c: ", asini_523/c)
f_down = spin_down(P_523, fspin, asini_523, 2456577.64636 + P_523*0.25, 2456577.64636)
print("min f_down: ", min(f_down))
print("max f_down: ", max(f_down))
z = z_param(min(f_down), 3*60)
print(z)
z = z_param(max(f_down), 3*60)
print(z)

# Test calculations 

q = 1.82
k2 = 219.1*1000
P = 0.86955*24*60*60

asini_1957 = asini(P, k2, q)
print("asini_1957/c: ", asini_1957/c)

f_down_max = 1.268e-5 
z = z_param(f_down_max, 3*60)
# print(z)




# tasc = 2456577.64636 # MJD
# t0 = 2456577.64636 + P_523*0.25

# f_down = spin_down(P_523, fspin, asini_523, t0, tasc)
# z = z_param(f_down, 3*60)
# print(z) 