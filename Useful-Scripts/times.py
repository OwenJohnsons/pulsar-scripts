#!/usr/bin/env python3
# Code Purpose: Print the time in various time zones of interest 

from datetime import datetime
from pytz import timezone

# Current time in UTC YYYY-MM-DD HH:MM:SS
now_utc = datetime.now(timezone('UTC'))
now_utc_str = now_utc.strftime('%H:%M:%S')
print(f"    UTC : {now_utc_str}")

# Ireland time
now_ireland = now_utc.astimezone(timezone('Europe/Dublin'))
now_ireland_str = now_ireland.strftime('%H:%M:%S')
print(f"Ireland : {now_ireland_str}")

# Pacific time
now_pacific = now_utc.astimezone(timezone('US/Pacific'))
now_pacific_str = now_pacific.strftime('%H:%M:%S')
print(f"Pacific : {now_pacific_str}")

# Eastern time
now_eastern = now_utc.astimezone(timezone('US/Eastern'))
now_eastern_str = now_eastern.strftime('%H:%M:%S')
print(f"Eastern : {now_eastern_str}")

# Parkes 
now_parkes = now_utc.astimezone(timezone('Australia/Sydney'))
now_parkes_str = now_parkes.strftime('%H:%M:%S')
print(f" Parkes : {now_parkes_str}")

