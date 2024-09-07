'''
Code Purpose: Convert Modified Julian Date to date and time and vice versa
Author: Owen A. Johnson
Date: 2024-09-07
Usage: python timeconv.py [-m MJD] [-d DATE]
'''
import argparse
import datetime
import time

def mjd_to_date(mjd):
    """
    Convert Modified Julian Date to date and time
    """
    # Convert MJD to Unix time
    unix_time = (mjd - 40587) * 86400
    # Convert Unix time to date and time
    date_time = datetime.datetime.utcfromtimestamp(unix_time)
    return date_time

def date_to_mjd(date_time):
    """
    Convert date and time to Modified Julian Date
    """
    # Convert date and time to Unix time
    unix_time = time.mktime(date_time.timetuple())
    # Convert Unix time to MJD
    mjd = unix_time / 86400 + 40587
    return mjd

def main():
    parser = argparse.ArgumentParser(description='Convert MJD to date and time and vice versa')
    parser.add_argument('-m', '--mjd', type=float, help='Modified Julian Date')
    parser.add_argument('-d', '--date', help='Date and time (YYYY-MM-DD HH:MM:SS)')
    args = parser.parse_args()
    
    if args.mjd:
        date_time = mjd_to_date(args.mjd)
        print('Date and time:', date_time)
    elif args.date:
        date_time = datetime.datetime.strptime(args.date, '%Y-%m-%d %H:%M:%S')
        mjd = date_to_mjd(date_time)
        print('Modified Julian Date:', mjd)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()