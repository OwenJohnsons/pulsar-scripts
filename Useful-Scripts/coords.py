#!/usr/bin/env python3
import astropy.units as u
import astropy.coordinates as coord
import argparse
from astropy.coordinates import SkyCoord

def parse_coordinates(ra, dec, input_type):
    """
    Parse RA and Dec based on the specified input type.
    """
    if input_type == 's':
        return SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
    elif input_type == 'd':
        return SkyCoord(ra=float(ra) * u.deg, dec=float(dec) * u.deg)
    elif input_type == 'r':
        return SkyCoord(ra=float(ra) * u.radian, dec=float(dec) * u.radian)
    elif input_type is 'g':
        return SkyCoord(l=float(ra) * u.deg, b=float(dec) * u.deg, frame='galactic')
    else:
        raise ValueError("Invalid input type. Use '-s' for sexagesimal, '-g' for galactic, '-d' for degrees, or '-r' for radians.")

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Convert RA and Dec to multiple formats')
    parser.add_argument('--name', type=str, help='Name of the target', required=False)
    parser.add_argument('-d', action='store_const', dest='input_type', const='d', help='Input in degrees')
    parser.add_argument('-r', action='store_const', dest='input_type', const='r', help='Input in radians')
    parser.add_argument('-s', action='store_const', dest='input_type', const='s', help='Input in sexagesimal (hh:mm:ss, dd:mm:ss)')
    parser.add_argument('-g', action='store_const', dest='input_type', const='g', help='Input in galactic coordinates')
    parser.add_argument('ra', nargs='?', type=str, help='Right Ascension')
    parser.add_argument('dec', nargs='?', type=str, help='Declination')
    
    args = parser.parse_args()
    
    # Resolve name if given
    if args.name:
        c = SkyCoord.from_name(args.name)
        print(f"Resolved coordinates for {args.name}:")
    elif args.input_type and args.ra and args.dec:
        c = parse_coordinates(args.ra, args.dec, args.input_type)
        print(f"Parsed coordinates:")
    else:
        parser.error("Either --name or (RA, Dec with -d, -r, or -h) must be provided.")
    
    # Print coordinates in different formats
    print(f"Sexagesimal:   {c.ra.to_string(unit=u.hourangle, sep=':', precision=4)}, {c.dec.to_string(unit=u.deg, sep=':',  precision=4)}")
    print(f"Degrees:       {c.ra.deg:.6f}°, {c.dec.deg:.6f}°")
    print(f"Radians:       {c.ra.radian:.6f}, {c.dec.radian:.6f} rad")
    print(f"Galactic:      {c.galactic.to_string()}")

if __name__ == '__main__':
    main()
