#!/usr/bin/env python3
'''
Code Purpose:
    - To get the current Local Sidereal Time (LST) at a given location. Default Birr Castle, Ireland.
Arguments: 
    - Optional: Latitude, Longitude, Time
'''

import argparse
import datetime
from astropy.time import Time

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
        now = Time(datetime.datetime.utcnow(), scale='utc')
    else:
        # Parse the input time (assumes it's given in UTC)
        try:
            time_obj = datetime.datetime.strptime(time, "%H:%M")
            now = Time(datetime.datetime.utcnow().replace(hour=time_obj.hour, minute=time_obj.minute, second=0), scale='utc')
        except ValueError:
            raise ValueError("Invalid time format. Use 'HH:MM'.")

    # Convert to LST
    lst = now.sidereal_time('apparent', longitude=long)
    return lst

def main():
    parser = argparse.ArgumentParser(description='Get the current Local Sidereal Time (LST) at a given location. Default: Birr Castle, Ireland.')
    parser.add_argument('--lat', type=float, default=53.2, help='Latitude of the location')
    parser.add_argument('--long', type=float, default=-7.9, help='Longitude of the location')
    parser.add_argument('--time', type=str, default='now', help="Time to get LST for in 'HH:MM' format (UTC), or 'now' for the current time.")
    args = parser.parse_args()

    lst = get_LST(args.long, args.time)
    print(lst)

if __name__ == '__main__':
    main()
