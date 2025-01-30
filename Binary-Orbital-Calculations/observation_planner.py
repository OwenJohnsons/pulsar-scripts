import configparser
import numpy as np
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from datetime import datetime
import argparse
import matplotlib.pyplot as plt
import scienceplots
plt.style.use('science')

def read_config(config_file):
    """
    Read in the configuration file and return the configuration data.
    
    Parameters:
        config_file (str): Path to the configuration file.
    
    Returns:
        dict: Configuration data as a dictionary.
    """
    config = configparser.ConfigParser()
    
    try:
        config.read(config_file)
        
        # Parse telescope section
        telescope = config['TELESCOPE'].get('telescope', 'Unknown')
        longitude = float(config['TELESCOPE'].get('longitude', '0.0'))
        latitude = float(config['TELESCOPE'].get('latitude', '0.0'))
        elevation_threshold = float(config['TELESCOPE'].get('elevation_threshold', '0.0'))
        
        # Validate longitude and latitude
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}")
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}")
        
        # Parse binary section
        source_name = config['BINARY'].get('source_name', 'Unknown')
        ra = float(config['BINARY'].get('ra', '0.0'))
        dec = float(config['BINARY'].get('dec', '0.0'))
        
        # Remove comments and convert to float
        orbital_period = float(config['BINARY'].get('orbital_period', '0.0').split('#')[0].strip())
        reference_time = float(config['BINARY'].get('reference_time', '0.0').split('#')[0].strip())
        
    except KeyError as e:
        print(f"Missing configuration key: {e}")
        raise
    except ValueError as e:
        print(f"Invalid value in configuration: {e}")
        raise
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        raise
    
    # Return configuration data as a dictionary
    return {
        'telescope': telescope,
        'longitude': longitude,
        'latitude': latitude,
        'elevation_threshold': elevation_threshold,
        'source_name': source_name,
        'ra': ra,
        'dec': dec,
        'orbital_period': orbital_period,
        'reference_time': reference_time
    }
    
def get_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Observation Planner')
    parser.add_argument('--ObsTime', type=str, help='Time of observation in YYYY-MM-DDTHH:MM format', default=datetime.now().strftime('%Y-%m-%dT%H:%M'))
    parser.add_argument('--ObsDuration', type=float, help='Duration of observation in hours', default=24)
    parser.add_argument('--Convention', type=str, help='Phase convention (optical, radio)', default='optical')
    return parser.parse_args()

def mjd2phase(mjd, mjd05, P_orb, convention):
    if convention == 'optical':
        return (((mjd - mjd05) / P_orb) - 0.5) % 1
    elif convention == 'radio': 
        return (((mjd - mjd05) / P_orb) - 0.25)  % 1
    
def main (): 

    # Read in the configuration file
    config = read_config('obs_parameter.config')
    parser = get_args()
    
    print('[TELESCOPE INFO]')
    print('Telescope: ', config['telescope'])
    print('Longitude: ', config['longitude'])
    print('Latitude: ', config['latitude'])
    print('Elevation Threshold: ', config['elevation_threshold'])
    print('Obs. Date: ', parser.ObsTime)
    print('Obs. MJD: ', Time(parser.ObsTime).mjd)
    print('\n')
    
    print('[BINARY INFO]')
    print('Source Name: ', config['source_name'])
    print('RA: ', config['ra'])
    print('DEC: ', config['dec'])
    print('Orbital Period: ', config['orbital_period'])
    print('Reference Time: ', config['reference_time'])
    print('Convention: ', parser.Convention)
    print('\n')
    
    # Set the location of the telescope
    location = EarthLocation.from_geodetic(lon=config['longitude']*u.deg, lat=config['latitude']*u.deg) 
    time = Time(parser.ObsTime)
    times = time + np.linspace(0, parser.ObsDuration, 100) * u.hour\

    # --- Calculate ALT/AZ coordinates --- 
    target = SkyCoord(ra=config['ra']*u.deg, dec=config['dec']*u.deg, frame='icrs')
    target_altaz = target.transform_to(AltAz(obstime=times, location=location))
    altitudes = target_altaz.alt.deg
    
    # --- Calculate the phase of the binary ---
    phases = mjd2phase(times.mjd, config['reference_time'], config['orbital_period'], parser.Convention)

    # --- Plotting ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, gridspec_kw={'height_ratios': [1, 1]})

    # Top plot: Altitude
    ax1.plot(times.datetime, altitudes, label="Altitude", color="blue")
    ax1.set_ylabel("Altitude (Deg°)")
    ax1.legend(loc="upper right")
    ax1.axhline(config['elevation_threshold'], color='red', linestyle='--', label='Elevation Threshold')
    ax1.grid(True)

    # Bottom plot: Phase
    ax2.plot(times.datetime, phases, label="Phase", color="green")
    ax2.set_ylabel("Phase")
    ax2.set_xlabel("Time (HH:MM)")
    ax2.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
    ax2.legend(loc="upper right")
    ax2.grid(True)

    plt.tight_layout()
    plt.show()
    
    
if __name__ == "__main__":
    main()
