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

def fit_func(x, a, b, c, d):
    return a*np.sin(b*x+c) + d 

phase, rot_vel = np.loadtxt('input/J0523-Strader-Fig3-extractd.txt', unpack=True, skiprows=1, usecols=(0,1), delimiter=',')

plt.figure(figsize=(4,4), dpi=200)
plt.scatter(phase, rot_vel, s=1, c='k', label = 'Strader et al. 2014')

phases = np.linspace(0, 1.5, 1000)
popt, pcov = curve_fit(fit_func, phase, rot_vel, p0=[1, 2*np.pi, 0, 0])
plt.plot(phases, fit_func(phases, *popt), c='r', lw=1, label='$A \sin(bx +c) + d$')
plt.xlabel('Phase')
plt.ylabel('Radial Velocity (km/s)')
plt.legend(loc = 'lower left', fontsize = 8)
plt.xlim(0,1.5)

plt.savefig('output/radial-velocity.png', bbox_inches='tight'); plt.show()
np.savetxt('output/radial-velocity.txt', np.transpose([phases, fit_func(phases, *popt)]), delimiter=',', header='Phase, Radial Velocity (km/s)', fmt='%1.3f')

# --- Gradient Calculation --- 
plt.figure(figsize=(4,4), dpi=200)
acceleration = np.diff(rot_vel)
plt.scatter(phase[0:-1], acceleration, c='k', s = 1)
plt.axhline(y = np.mean(acceleration), color = 'r', lw = 1, label = 'Mean Diff')

plt.xlabel('Phase')
plt.ylabel('Acceleration (km/s$^2$)')

# --- Jerk Calculation ---
plt.figure(figsize=(4,4), dpi=200)
jerk = np.diff(acceleration)

# %%
