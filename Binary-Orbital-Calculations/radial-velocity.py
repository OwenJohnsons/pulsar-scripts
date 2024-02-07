'''
Code Purpose:
Author: Owen A. Johnson
Date: 2023-09-18
'''
#%%
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scienceplots 
plt.style.use('science')

# --- Known Parameters ---
orbital_period = 16.5
omega_b = 2*np.pi/orbital_period

def fit_func(x, a, b, c, d):
    return a*np.cos(b*x+c) + d 

phase, rot_vel = np.loadtxt('input/J0523-Strader-Fig3-extractd.txt', unpack=True, skiprows=1, usecols=(0,1), delimiter=',')

plt.figure(figsize=(4,4), dpi=200)
plt.scatter(phase, rot_vel, s=1, c='k', label = 'Strader et al. 2014')

phases = np.linspace(0, 1.5, 2000)
popt, pcov = curve_fit(fit_func, phase, rot_vel, p0=[200, omega_b, 0, 0])
plt.plot(phases, fit_func(phases, *popt), c='r', lw=1, label='$A \cos(\Omega_b t + \phi)$')
plt.xlabel('Phase')
plt.ylabel('Radial Velocity (km/s)')
plt.legend(loc = 'lower left', fontsize = 8)
# plt.xlim(0,1.5)t

plt.savefig('output/radial-velocity.png', bbox_inches='tight'); plt.show()
np.savetxt('output/radial-velocity.txt', np.transpose([phases, fit_func(phases, *popt)]), delimiter=',', header='Phase, Radial Velocity (km/s)', fmt='%1.3f')

def acceleration(x, a, b, c):
    return a*b*np.cos(b*x+c)

plt.figure(figsize=(4,4), dpi=200)
plt.plot(phases, acceleration(phases, *popt[:-1]), c='r', lw=1, label='$A \cos(\Omega_b t + \phi)$')

plt.xlabel('Phase')
plt.ylabel('Acceleration (km/s$^2$)')
# %%
