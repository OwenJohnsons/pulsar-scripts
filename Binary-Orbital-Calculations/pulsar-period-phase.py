'''

'''
#%%
from astropy.time import Time
import numpy as np
from numpy import sin, cos, pi, linspace
import pandas as pd
import matplotlib.pyplot as plt
from math import cos, sin, hypot
import scienceplots 
plt.style.use(['science'])
# import smplotlib

def bjd_to_date_time(bjd):
    # BJD is usually given in TDB (Barycentric Dynamical Time)
    t = Time(bjd, format='jd', scale='tdb')
    
    # Convert to UTC (Coordinated Universal Time) for human-readable date and time
    t_utc = t.utc
    
    return t_utc.iso

def date_time_to_bjd(date_time):
    # Convert to Time object
    t = Time(date_time, format='iso', scale='utc')
    # Convert to BJD (Barycentric Julian Date)
    bjd = t.tdb.jd
    
    return bjd

def orbital_phase_calc(ephermeris, reference_phase, orbital_period, time):
    '''
    ephemeris: BJD at reference phase
    reference_phase: orbital phase at ephemeris
    orbital_period: orbital period in hours
    time: BJD of observation
    returns: orbital phase at time of observation
    '''
    delta_hours = (time - ephermeris)*24
    phase = (delta_hours/orbital_period) - int(delta_hours/orbital_period) + reference_phase
    if phase > 1:
        phase -= 1
    return phase

def plot_orbit(radius):
    angles = linspace(0 * pi, 2 * pi, 100 )
    xs = radius * np.cos(angles)
    ys = radius * np.sin(angles)
    plt.plot(xs, ys, color = 'black')

def plot_arc(radius, start_per, end_per):

    plt.plot([0, radius * np.cos(2*pi*start_per)], [0, radius * np.sin(2*pi*start_per)], color = "red")
    plt.plot([0, radius * np.cos(2*pi*end_per)], [0, radius * np.sin(2*pi*end_per)], color = "red")

    arc_angles = linspace(2*pi*start_per, 2*pi*end_per, 100)
    arc_xs = radius * np.cos(arc_angles); arc_ys = radius * np.sin(arc_angles)
    plt.plot(arc_xs, arc_ys, color = 'red', lw = 3)
    # plt.fill_between(arc_xs, arc_ys, color='red', alpha=0.5, hatch='//', edgecolor='red', lw=0)


obs_times = np.loadtxt('input/J0523-Parkes-Observation-Times.txt', dtype='str')

orbital_period = 16.5 # hours
reference_phase = 0.5 # orbital phase at ephemeris
ephermeris = 2456577.64636 # BJD at orbital phase 0.5

phases = [] # orbital phases of observations

for i in range(len(obs_times)):
    datetime = obs_times[i][0] + ' ' + obs_times[i][1]
    bjd = date_time_to_bjd(datetime)
    phase = orbital_phase_calc(ephermeris, reference_phase, orbital_period, bjd)
    print(datetime, phase)
    phases.append(phase)


plt.figure(figsize = (10, 10), dpi = 200)#draw point at orgin
plt.scatter(0, 0, s=600, zorder = 5, color = 'blue', label = 'J0523')

r = 1.5
plot_orbit(r)
coverage = 0

for i in range(len(phases)//2):
    plot_arc(r, phases[i*2], phases[i*2+1])
    window_length = abs(phases[i*2+1] - phases[i*2])
    coverage += window_length

plt.annotate('Coverage: ' + str(round(coverage, 2)) + ' orbits', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=12)
plt.annotate('Orbital Period: ' + str(orbital_period) + ' hours', xy=(0.05, 0.9), xycoords='axes fraction', fontsize=12)
plt.annotate('$T_{0.5}$: ' + str(ephermeris) + ' d', xy=(0.05, 0.85), xycoords='axes fraction', fontsize=12)
plt.annotate('Source: J0523', xy=(0.05, 0.8), xycoords='axes fraction', fontsize=12)

# --- Annotate orbital phases ---
phase_labels = [0.25, 0.5, 0.75, 1]
r = 1.65
for i in range(len(phase_labels)):
    plt.annotate(str(phase_labels[i]), xy=(r * np.cos(2*pi*(phase_labels[i] + reference_phase)), r * np.sin(2*pi*phase_labels[i])), xycoords='data', fontsize=12)


plt.xticks([])
plt.yticks([])

plt.xlim(-2, 2)
plt.ylim(-2, 2)
plt.gca().set_aspect('equal')
plt.show()

# --- Sine Wave Phase Variation --- 

plt.figure(figsize = (6, 6), dpi = 200)

time = np.linspace(0, orbital_period, 1000)
sine_wave = np.sin(2*pi*time/orbital_period + reference_phase)

count = 0 
for i in range(len(phases)//2):
    if phases[i*2] > phases[i*2+1]:
        # sine wave values between phases[i*2] and phases[i*2+1]
        mask = (sine_wave >= phases[i*2+1]) & (sine_wave <= phases[i*2])
        plt.scatter(time[mask], sine_wave[mask], color = 'k', lw = 1, zorder = 3, s = 10)
        count += len(sine_wave[mask])
    else:
        mask = (sine_wave >= phases[i*2]) & (sine_wave <= phases[i*2+1])
        plt.scatter(time[mask], sine_wave[mask], color = 'k', lw = 1, zorder = 3, s = 10)
        count += len(sine_wave[mask])

plt.annotate('Coverage: ' + str(round((count/len(sine_wave)), 2)) + '$\%$', xy=(0.63, 0.87), xycoords='axes fraction', fontsize=12)


plt.plot(time, sine_wave, color = '#0569b9', lw = 5, label = 'Orbit Covered')
plt.xlabel('Orbital Period [hrs]')
plt.ylabel('Orbital Phase') 
plt.legend(fontsize = 12)
plt.savefig('output/sine-wave-coverage.png', bbox_inches='tight'); plt.show()


#%%

for i in range(len(phases)//2):
    if phases[i*2] > phases[i*2+1]:
        phases[i*2+1] += 1 
    else: 
        pass 


# Create a Gantt chart
fig, ax = plt.subplots(figsize=(10, 5))

labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

for i in range(len(phases)//2):
    ax.barh(labels[i], phases[i*2+1] - phases[i*2], left=phases[i*2], label=f"Phase {phases[i]}")

# # Set labels and title
ax.set_xlabel("Phase $(\phi)$")
ax.set_ylabel("Observation Run")
# ax.set_xlim(0, 1.6)

# Display the Gantt chart
plt.show()