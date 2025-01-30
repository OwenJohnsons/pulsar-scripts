#!/usr/bin/env python3
'''
Code Purpose:
    - To get the current Local Sidereal Time (LST) at a given location. Default Birr Castle, Ireland.
Arguments: 
    - Optional: Latitude, Longitude
'''

import argparse 
import datetime
from astropy.time import Time

def get_LST(long):
    # Get the current time in UTC
    now = Time(datetime.datetime.now(), scale='utc')
    # Convert to LST
    lst = now.sidereal_time('apparent', longitude=long)
    return lst

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Get the current Local Sidereal Time (LST) at a given location.')
    parser.add_argument('--lat', type=float, default=53.2, help='Latitude of location')
    parser.add_argument('--long', type=float, default=-7.9, help='Longitude of location')
    args = parser.parse_args()
    # Get LST
    lst = get_LST(args.long)
    print(lst)
    
if __name__ == '__main__':
    main()
