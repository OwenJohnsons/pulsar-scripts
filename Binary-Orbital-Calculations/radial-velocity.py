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
plt.plot(phases, fit_func(phases, *popt), c='#0569b9', lw=1, label='Keplerian Fit')
plt.xlabel('Phase $(\phi)$')
plt.ylabel('Radial Velocity [km/s]')
plt.legend(loc = 'lower left', fontsize = 8)
# plt.xlim(0,1.5)t

plt.savefig('output/radial-velocity.png', bbox_inches='tight'); plt.show()
np.savetxt('output/radial-velocity.txt', np.transpose([phases, fit_func(phases, *popt)]), delimiter=',', header='Phase, Radial Velocity (km/s)', fmt='%1.3f')

plt.figure(figsize=(4,4), dpi=200)
plt.plot(phases, fit_func(phases, *popt), c='#0569b9', lw=1, label='Keplerian Fit')
plt.xlim(0.5,0.6)
# %%
import numpy as np
from matplotlib import cbook
from matplotlib import pyplot as plt

fig, ax = plt.subplots(dpi = 200, figsize=(4,6))

# make data

ax.plot(phases, fit_func(phases, *popt), c='#0569b9', lw=1, label='Keplerian Fit')
ax.scatter(phase, rot_vel, s=1, c='k', label = 'Strader et al. 2014')

# inset axes....
x1, x2, y1, y2 = 0.5, 0.51, 0, 50  # subregion of the original image
sizes = 0.3
axins = ax.inset_axes(
    [0.05, 0.1, 0.2, sizes],
    xlim=(x1, x2), ylim=(y1, y2), xticklabels=[], yticklabels=[])
axins.plot(phases, fit_func(phases, *popt), c='#0569b9', lw=1, label='Keplerian Fit')
ax.indicate_inset_zoom(axins, edgecolor="black")

x1, x2, y1, y2 = 1.2, 1.21, 200, 250  # subregion of the original image
axins = ax.inset_axes(
    [0.7, 0.1, 0.2, sizes],
    xlim=(x1, x2), ylim=(y1, y2), xticklabels=[], yticklabels=[])
axins.plot(phases, fit_func(phases, *popt), c='#0569b9', lw=1, label='Keplerian Fit')
axins.scatter(phase, rot_vel, s=1, c='k', label = 'Strader et al. 2014')
ax.indicate_inset_zoom(axins, edgecolor="black")

plt.xlabel('Phase $(\phi)$')
plt.ylabel('Radial Velocity [km/s]')
plt.legend(loc = 'lower right', fontsize = 8, frameon=True)

plt.show()


# %%
