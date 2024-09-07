''' 
Code Purpose: 
Author: Owen A. Johnson
Date: 2024-09-07
Usage: python coords2deg.py --name <name> 
'''

import astropy.units as u
import astropy.coordinates as coord
import argparse
from astropy.coordinates import SkyCoord

# - Parse Arguments -
parser = argparse.ArgumentParser(description='Convert RA and Dec to Degrees from a given target name')
parser.add_argument('--name', type=str, help='Name of the target', required=True)

args = parser.parse_args()
name = args.name
print('Target:', name)

c = SkyCoord.from_name(name)
print(c.ra.degree, c.dec.degree)