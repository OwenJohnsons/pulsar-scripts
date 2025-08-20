# Plot altitude of the sun above the horizon for a given location and time
#%%
import numpy as np
import matplotlib.pyplot as plt
import datetime
import astropy.units as u
from astropy.coordinates import EarthLocation, AltAz, get_sun
from astropy.time import Time
import scienceplots
plt.style.use(['science', 'grid'])

# Location
name = "Birr"
latitude = 53.095
longitude = 7.913
elevation = 12

# Time: UTC now 
now = datetime.datetime.utcnow()
time = Time(now)

location = EarthLocation(lat=latitude, lon=longitude, height=elevation)
obs_length = 7 # days
delta = np.linspace(0, obs_length, 1000)*u.day
time = time + delta

sun = get_sun(time)
altaz = sun.transform_to(AltAz(obstime=time, location=location))
altitude = altaz.alt.deg

plt.figure(figsize=(10, 6))

dates = [t.datetime for t in time]  # Convert to datetime objects

plt.plot(dates, altitude)
plt.title(f"Sun Altitude Above Horizon for {name} starting from {now}", fontsize=14)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Altitude (degrees)", fontsize=12)
plt.grid()
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.tight_layout()
plt.ylim(0, 30)
plt.show()

