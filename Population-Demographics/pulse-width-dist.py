#%%
'''
Code Purpose: Plot distribution of Pulse Widths from ATNF. 
Author: Owen A. Johnson
Date: 12/01/2024
'''

import numpy as np 
import matplotlib.pyplot as plt
import scienceplots; plt.style.use(['science','ieee']); ibm_cols = ['#6490ff', '#795ef0', '#dc5880', '#fe6100', '#ffae00']
import pandas as pd
from psrqpy import QueryATNF
from astropy.table import Table
import matplotlib.image as mpimg
from scipy import stats

query = QueryATNF(params=['NAME', 'W50', 'W10', 'DM']) # Query the ATNF pulsar catalogue for the following parameters: P0, P1, BINARY, TYPE, P1_I

table = query.table.to_pandas() # The table of ATNF pulsars
# drop W50 values that are NaN
table = table.dropna(subset=['W50'])

# --- Plotting the Pulse Widths ---
plt.figure(figsize=(5,4), dpi=200) # Set the figure size

plt.hist(table['W50'], bins=50, alpha=1, facecolor='grey', edgecolor='black', linewidth=0.5)
plt.ylabel('Number of Pulsars')
plt.xlabel('Width of pulse at 50\% of peak [ms]')
plt.axvline(np.mean(table['W50']), color='blue', linestyle='dashed', linewidth=1, label='Mean, %.2f ms' % np.mean(table['W50']))
plt.axvline(np.mean(table['W50']) + np.std(table['W50']), color='green', linestyle='dotted', linewidth=1, label='1$\sigma$, %.2f ms' % np.std(table['W50']))
plt.axvline(np.max(table['W50']), color='red', linestyle='dotted', linewidth=1, label='Max, %.2f ms' % np.max(table['W50']))

query_ms = 100
plt.annotate('Percentage of Pulsars with W50 $\leq$ %s ms: %.2f' % (query_ms, (len(table[table['W50'] < query_ms])/len(table))), xy=(0.5, 0.9), xycoords='axes fraction', fontsize=8, ha='center', va='center')

plt.legend()
plt.title('Distribution of Pulse Widths from ATNF')


plt.figure(figsize=(5,4), dpi=200) # Set the figure size

plt.hist(table['DM'], bins=50, alpha=1, facecolor='grey', edgecolor='black', linewidth=0.5)
plt.ylabel('Number of Pulsars')
plt.xlabel('Dispersion Measure [cm$^{-3}$ pc]')

plt.axvline(np.mean(table['DM']), color='blue', linestyle='dashed', linewidth=1, label='Mean, %.2f cm$^{-3}$ pc' % np.mean(table['DM']))
plt.axvline(np.mean(table['DM']) + np.std(table['DM']), color='green', linestyle='dotted', linewidth=1, label='1$\sigma$, %.2f cm$^{-3}$ pc' % np.std(table['DM']))
plt.axvline(np.max(table['DM']), color='red', linestyle='dotted', linewidth=1, label='Max, %.2f cm$^{-3}$ pc' % np.max(table['DM']))

plt.legend()