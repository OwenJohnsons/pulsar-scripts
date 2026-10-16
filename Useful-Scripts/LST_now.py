#!/usr/bin/env python3
'''
Code Purpose:
    - To get the current Local Sidereal Time (LST) for the configured sites.
Arguments: 
    - Optional: Custom latitude, custom longitude, time
'''

import argparse
import datetime
import astropy.units as u
from astropy.time import Time

def get_observation_time(time='now'):
    """Return the UTC time used for the LST calculation."""
    now = datetime.datetime.now(datetime.timezone.utc)
    if time == 'now':
        return Time(now, scale='utc')

    try:
        time_obj = datetime.datetime.strptime(time, "%H:%M")
    except ValueError as exc:
        raise ValueError("Invalid time format. Use 'HH:MM'.") from exc

    return Time(
        now.replace(
            hour=time_obj.hour,
            minute=time_obj.minute,
            second=0,
            microsecond=0,
        ),
        scale='utc',
    )


def get_LST(long, time='now'):
    """
    Calculate the Local Sidereal Time (LST) at a given longitude.

    Args:
    - long (float): Longitude of the location.
    - time (str): Optional. Time in 'HH:MM' format or 'now' for current time.

    Returns:
    - lst (astropy.coordinates.Angle): The local sidereal time.
    """
    now = get_observation_time(time)
    lst = now.sidereal_time('apparent', longitude=long)
    return lst


def main():
    parser = argparse.ArgumentParser(description='Get the current Local Sidereal Time (LST) for each configured site.')
    parser.add_argument('-lat', type=float, help='Custom latitude in degrees')
    parser.add_argument('-long', type=float, help='Custom longitude in degrees')
    parser.add_argument('--time', type=str, default='now', help="Time to get LST for in 'HH:MM' format (UTC), or 'now' for the current time.")
    args = parser.parse_args()

    if (args.lat is None) != (args.long is None):
        parser.error('-lat and -long must be provided together.')

    # --- Site Dictionary ---
    site_dict = {
        'IE613': {
            'longitude': 7.9219,
            'latitude': 53.0950,
            'elevation': 72.0,
            'timezone': 'Europe/Dublin',
        },
        'LWA': {
            'longitude': -118.281699,
            'latitude': 37.239870,
            'elevation': 1200.0,
            'timezone': 'America/Los_Angeles',
        },
    }

    observation_time = get_observation_time(args.time)
    utc_time = observation_time.to_datetime(timezone=datetime.timezone.utc)
    print(f"UTC: {utc_time:%Y-%m-%d %H:%M:%S} UTC")
    print("\nLocal Sidereal Time:")

    for site_name, site in site_dict.items():
        longitude = site['longitude'] * u.deg
        lst = observation_time.sidereal_time('apparent', longitude=longitude)
        lst_string = lst.to_string(
            unit=u.hourangle,
            sep=':',
            precision=2,
            pad=True,
        )
        print(f"  {site_name:<8} {lst_string}  "
              f"(latitude {site['latitude']:+.4f}°, longitude {site['longitude']:+.4f}°)")

    if args.lat is not None and args.long is not None:
        custom_lst = observation_time.sidereal_time(
            'apparent',
            longitude=args.long * u.deg,
        )
        custom_lst_string = custom_lst.to_string(
            unit=u.hourangle,
            sep=':',
            precision=2,
            pad=True,
        )
        print(f"\nCustom location: LST {custom_lst_string}  "
              f"(latitude {args.lat:+.4f}°, longitude {args.long:+.4f}°)")

if __name__ == '__main__':
    main()
