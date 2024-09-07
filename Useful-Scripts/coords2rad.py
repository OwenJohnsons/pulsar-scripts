#%% 
'''
Usage: python coords2rad.py --name <name>
'''
import astropy.units as u
import astropy.coordinates as coord
import argparse 
from astropy.coordinates import SkyCoord

# - Parse Arguments -
parser = argparse.ArgumentParser(description='Convert RA and Dec to Radians')
parser.add_argument('--name', type=str, help='Name of the target', required=True)
args = parser.parse_args(); name = args.name
print('Target:', name)

c = SkyCoord.from_name(name)
print(c.ra.radian, c.dec.radian)