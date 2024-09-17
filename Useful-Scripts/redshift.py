'''
Code Purpose: Convert a target name to its redshift value
Author: Owen A. Johnson
Date: 2024-09-07
Usage: python redshift.py --name <name>
'''

import argparse
from astroquery.ipac.ned import Ned
from astropy.coordinates import SkyCoord

# - Parse Arguments -
parser = argparse.ArgumentParser(description='Retrieve the redshift of a given target name from NED')
parser.add_argument('--name', type=str, help='Name of the target', required=True)

args = parser.parse_args()
name = args.name
print('Target:', name)

# Query NED for the object by name
try:
    result_table = Ned.query_object(name)
    redshift = result_table['Redshift'][0]
    print(f"Name: {name}")
    print(f"Redshift: {redshift}")
except Exception as e:
    print(f"Error retrieving redshift for {name}: {e}")