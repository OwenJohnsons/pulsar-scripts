#!/usr/bin/env python3
'''
Code Purpose: Plot elevation and sensitivity plots for a given target at a given observation window for IE613 
Author: Owen A. Johnson
Date: 2024-03-05
'''

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates
import astropy.units as u
import numpy as np
import argparse
import os 
# import scienceplots; plt.style.use(['science', 'no-latex'])
import smplotlib

from astropy.coordinates import EarthLocation, SkyCoord, solar_system_ephemeris, get_body, AltAz
from astropy.time import Time
from astroplan import Observer, FixedTarget
from astroplan.plots import plot_sky
import datetime
from datetime import datetime

def get_LST(long, time='now'):
    """
    Calculate the Local Sidereal Time (LST) at a given longitude.

    Args:
    - long (float): Longitude of the location.
    - time (str): Optional. Time in 'HH:MM' format or 'now' for current time.

    Returns:
    - lst (astropy.coordinates.Angle): The local sidereal time.
    """
    if time == 'now':
        # Use the current UTC time
        now = Time(datetime.now(), scale='utc')
    else:
        # Parse the input time (assumes it's given in UTC)
        try:
            time_obj = datetime.strptime(time, "%H:%M")
            now = Time(datetime.now().replace(hour=time_obj.hour, minute=time_obj.minute, second=0), scale='utc')
        except ValueError:
            raise ValueError("Invalid time format. Use 'HH:MM'.")

    # Convert to LST
    lst = now.sidereal_time('apparent', longitude=long)
    return lst

# ------------------------------------
#          - Set up Arguments -
# ------------------------------------
parser = argparse.ArgumentParser(description='Plot elevation and sensitivity plots for a given target')
parser.add_argument('--name', type=str, help='Name of the target', required=True)
parser.add_argument('--date', help='Date of observation in form YYYY-MM-DD HH:MM:SS', default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
parser.add_argument('--sens', help="Plot sensitivity curve of observation", action='store_true')
parser.add_argument('ra', type=float, help='Right Ascension of the target in radians or degrees', nargs='?')
parser.add_argument('dec', type=float, help='Declination of the target in radians or degrees', nargs='?')

args = parser.parse_args()

# --- Check if the date is in the correct format ---
try:
    observe_time = args.date
    trgt_name = args.name
    datetime.strptime(observe_time, '%Y-%m-%d %H:%M:%S')
except ValueError:
    raise ValueError("Incorrect date format, should be YYYY-MM-DD HH:MM:SS")

# --- Check if ra and dec are provided ---
if args.ra and args.dec:
    # check if in radians or degrees 
    if args.ra > 2*np.pi:
        ra_deg = args.ra * u.deg
        print("RA in degrees:", ra_deg)
    else:
        ra_rad = args.ra * u.rad
        ra_deg = ra_rad.to(u.deg)
        print("RA in radians:", ra_rad)
    if np.abs(args.dec) > 2*np.pi:
        dec_deg = args.dec * u.deg
        print("Dec in degrees:", dec_deg)
    else:
        dec_rad = args.dec * u.rad
        dec_deg = dec_rad.to(u.deg)
        print("Dec in radians:", dec_rad)
else:
    if trgt_name == 'Sun' or trgt_name == 'sun':
        print('Sun selected, no need for RA and Dec.')
        pass
    else:
        print('No RA and Dec provided, asking simbad and PSRCAT for coordinates for %s...' % trgt_name)

        from psrqpy import QueryATNF
        from astropy.table import Table
        query = QueryATNF(params=['NAME', 'RaJ', 'DecJ']) 
        table = query.table.to_pandas()
        
        if trgt_name in table['NAME'].values:
            print(table.loc[table['NAME'] == trgt_name])
            ra = table.loc[table['NAME'] == trgt_name, 'RAJ'].values[0]
            dec = table.loc[table['NAME'] == trgt_name, 'DECJ'].values[0]
            trgt = SkyCoord(ra=ra, dec=dec, unit=(u.hourangle, u.deg))
            ra_deg = trgt.ra.degree * u.deg; dec_deg = trgt.dec.degree * u.deg
        
        else:
            from astroquery.simbad import Simbad
            result_table = Simbad.query_object(trgt_name)
            print(result_table)

            if result_table is None:
                raise ValueError('No coordinates found for %s' % trgt_name)
        
            trgt = SkyCoord(ra=result_table['RA'], dec=result_table['DEC'], unit=(u.hourangle, u.deg))
            # convert to degrees
            ra_deg = trgt.ra.degree * u.deg
            dec_deg = trgt.dec.degree * u.deg
            
        print('Coordinates found for %s: %s, %s' % (trgt_name, ra_deg, dec_deg))


# ------------------------------------
#          - Set up Observer -
# ------------------------------------

# Set up Observer, Target and observation time objects.
longitude = 7.9219 * u.deg
latitude = 53.0950 * u.deg
elevation = 72.0 * u.m
location = EarthLocation.from_geodetic(longitude, latitude, elevation)
print('CURRENT LST:', get_LST(longitude))

observer = Observer(name='I-LOFAR',
               location=location,
               pressure=0.615 * u.bar,
               relative_humidity=0.11,
               temperature=0 * u.deg_C,
               description="LOFAR Station IE613")

observe_time = Time(args.date); print('Observation start time:', observe_time)
obs_window = 31; print('Observation window:', obs_window, 'hours')
increment = obs_window / 1000; print('Time increment:', increment, 'minutes')  # Divide the window into 1000 increments
observe_times = observe_time + np.linspace(0, obs_window, 1000) * u.hour

# ------------------------------------
#          - Benchmark Targets -
# ------------------------------------

# - Polaris -
coordinates = SkyCoord('02h31m49.09s', '+89d15m50.8s', frame='icrs')
polaris = FixedTarget(name='Polaris', coord=coordinates)
polaris_style = {'color': 'k', 'marker': '*'}

# - Crab Pulsar - 
coordinates = SkyCoord('05h34m31.93830s', '+22d00m52.1758s', frame='icrs')
crab = FixedTarget(name='Crab', coord=coordinates)
crab_style = {'color': 'r','marker': 'o'}

# - Sun - 
with solar_system_ephemeris.set('builtin'):
    sun_coords = get_body('sun', observe_times, location) 
sun = FixedTarget(name='Sun', coord=sun_coords)
sun_style = {'color': 'y'}

# - Custom Target - 
if trgt_name == 'Sun':
    print('Sun selected, no need for custom target alt-az plotting.')
    alt = sun_coords.transform_to(AltAz(obstime=observe_times, location=location)).alt.degree
    az = sun_coords.transform_to(AltAz(obstime=observe_times, location=location)).az.degree
else:
    coord_deg = SkyCoord(ra=ra_deg, dec=dec_deg)
    custom_target = FixedTarget(name=trgt_name, coord=coord_deg)
    custom_style = {'color': 'b'}
    alt = coord_deg.transform_to(AltAz(obstime=observe_times, location=location)).alt.degree
    az = coord_deg.transform_to(AltAz(obstime=observe_times, location=location)).az.degree

# ------------------------------------
#        - Plotting Results -
# ------------------------------------
plot_sky(polaris, observer, observe_time, style_kwargs=polaris_style)
plot_sky(crab, observer, observe_times, style_kwargs=crab_style)
plot_sky(sun, observer, observe_times, style_kwargs=sun_style)
if trgt_name != 'Sun':
    plot_sky(custom_target, observer, observe_times, style_kwargs=custom_style)
plt.legend(loc='center left', bbox_to_anchor=(1.05, 0.5))
plt.savefig('sky-plot.png', dpi=200)
plt.close()

#%%
plt.figure(figsize=(20, 8))
# Creating subplots with shared x-axis
ax1 = plt.subplot(2, 2, 1)
ax2 = plt.subplot(2, 2, 3, sharex=ax1)
ax3 = plt.subplot(1, 2, 2)

# Plotting azimuth
ax1.plot(observe_times.datetime, az, label='Azimuth', color='black')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1.xaxis.set_major_locator(mdates.HourLocator(interval=7))
ax1.set_ylabel('Azimuth')
ax1.legend(frameon=True)
# hide xticks 
plt.setp(ax1.get_xticklabels(), visible=False)
ax1.grid(True)

# Plotting altitude

# Find where altitude is max_alt - 10 on either side
max_alt_index = np.where(alt == np.max(alt))[0][0]
max_alt = np.max(alt)

# Check if the max altitude is greater than 30 degrees
if max_alt > 30:
    print(f"Max altitude ({max_alt}) is greater than 30°, finding where it crosses 30° instead of max-10°.")

    # Find where altitude crosses 30 degrees before and after the max altitude
    try:
        before_max_index = np.where(alt[:max_alt_index] <= 30)[0][-1]
    except IndexError:
        before_max_index = None
        print("No altitude crossing below 30° before the max altitude")

    try:
        after_max_index = np.where(alt[max_alt_index:] <= 30)[0][0] + max_alt_index
    except IndexError:
        after_max_index = None
        print("No altitude crossing below 30° after the max altitude")
else:
    print(f"Max altitude ({max_alt}) is less than or equal to 30°, using max-10° rule.")

    # Initialize variables for before and after max
    before_max_index, after_max_index = None, None

    # Try to find the 10° drop points, handle out-of-bounds exceptions
    try:
        before_max_index = np.where(alt[:max_alt_index] <= max_alt - 10)[0][-1]
    except IndexError:
        print("No altitude drop by 10° before the max altitude")

    try:
        after_max_index = np.where(alt[max_alt_index:] <= max_alt - 10)[0][0] + max_alt_index
    except IndexError:
        print("No altitude drop by 10° after the max altitude")

# Plot the altitude and vertical lines if the indices are found
ax2.plot(observe_times.datetime, alt, label='Altitude', color='black')

# plot max altitude time 
ax2.axvline(observe_times.datetime[max_alt_index], label=f'Max Alt at {observe_times.datetime[max_alt_index].strftime("%H:%M")}', color='blue')
if before_max_index is not None:
    ax2.axvline(observe_times.datetime[before_max_index], color='g', linestyle='--', label=f'Crossed 30° before max at {observe_times.datetime[before_max_index].strftime("%H:%M")}')
if after_max_index is not None:
    ax2.axvline(observe_times.datetime[after_max_index], color='g', linestyle='--', label=f'Crossed 30° after max at {observe_times.datetime[after_max_index].strftime("%H:%M")}')
    
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax2.xaxis.set_major_locator(mdates.HourLocator(interval=4))
ax2.axhline(0, color='r', linestyle='--', label='Horizon')
ax2.set_xlabel('Time')
ax2.set_ylabel('Altitude')
ax2.legend(frameon=True, fontsize=8)
ax2.grid(True)

# Displaying image
img = mpimg.imread('sky-plot.png')
flipped_img = np.flipud(img)  # Flip image vertically
ax3.imshow(flipped_img)
ax3.axis('off')  # Hide axes for the image

day_of_month = observe_time.datetime.day  # Get day of the month
day_suffix = "th"  # Default to "th"

if 4 <= day_of_month <= 20 or 24 <= day_of_month <= 30:
    day_suffix = "th"
else:
    day_suffix = ["st", "nd", "rd"][day_of_month % 10 - 1]
day_name = observe_time.datetime.strftime("%A")  # Get day name in word format
month = observe_time.datetime.strftime("%B")  # Get month in word format

# Concatenate day, day of the month, and month in the desired format
date_string = f"{day_name}, {month}, {day_of_month}{day_suffix}"

plt.suptitle('%s observation from IE613 starting %s' % (trgt_name, date_string), fontsize=16)
plt.tight_layout()
# plt.savefig('./elevation-plots/%s-elevation-plot-%s.png' % (trgt_name, (str(day_of_month) + str(month))), dpi=200)
plt.show()

if args.sens: 
    import subprocess
    
    ra_hms = coord_deg.ra.to_string(unit=u.hourangle, sep=':', precision=2)
    dec_dms = coord_deg.dec.to_string(unit=u.degree, sep=':', precision=2)
    
    command = command = 'python ./tsky_sefd_LOFAR_ilt.py --ra %s --dec %s --freqs 100 110 120 130 140 150 160 170 180 190' % (ra_hms, dec_dms)
    output = subprocess.check_output(command, shell=True).decode('utf-8')
    
    freq = []; conv_temp = []; raw_temp = []; diff_temp = []
    lines = output.strip().split('\n')
    lofar_bandwidth = 3.66e6 # Hz
    tobs_v = 2*3600 # seconds
    
    for line in lines[4:]:
        # Split each line by tabs
        columns = line.split('\t')
        # print(columns)
        freq.append(float(columns[0].split(':')[0]))
        print(columns[0].split(':')[0]) 
        conv_temp.append(float(columns[2]))
        raw_temp.append(float(columns[4]))
        diff_temp.append(float(columns[6]))
        
    freq = np.array(freq); conv_temp = np.array(conv_temp); raw_temp = np.array(raw_temp); diff_temp = np.array(diff_temp)
    Aeff = np.linspace(2400, 1422, len(freq))
    def sens_limit(snr, tsys, Aeff, bandwidth, tobs): 
        num = snr*tsys*1380*2
        print(num)
        dom = (Aeff*(np.sqrt(2*tobs*bandwidth)))  
        print(dom)
        return num/dom
    
    smin = sens_limit(8, conv_temp, Aeff, lofar_bandwidth, tobs_v)
    
    print('Sensitivity Limit (mJy):', 1000*smin.min())
    plt.figure(figsize=(6, 3), dpi = 200)
    plt.axhline(1000*smin.min(), color='r', linestyle='--', label='Min Sensitivity (%s mJy)' % round(1000*smin.min(), 2))
    plt.plot(freq, smin*1000, 'o-')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Sensitivity Limit (mJy)')
    plt.title('Sensitivity limit for %s' % (trgt_name), fontsize=12)
    plt.legend()
    plt.savefig('./elevation-plots/%s-sensitivity-plot.png' % (trgt_name), dpi=200)
    plt.show()