'''
Author: Owen A. Johnson
Date: 26/11/2024
Code Purpose:
'''

import numpy as np
import riptide as rt
from riptide import ffa_search
import matplotlib
matplotlib.use('TkAgg')

tseries_presto = rt.TimeSeries.from_presto_inf("/fred/oz203/data/PX094/J0523-2529/frequency_split/uwl_221109_114040_0/prepdata/0.7-1.9GHz/uwl_221109_114040_0.add_0.7-1.9GHz_prepsub_DM23.61_red.inf")

# Compute periodogram
ts, plan, pgram = ffa_search(tseries_presto, rmed_width=4.0, period_min=1.0, period_max=10.0, bins_min=240, bins_max=260)

# Plot S/N vs. trial period
pgram.display()