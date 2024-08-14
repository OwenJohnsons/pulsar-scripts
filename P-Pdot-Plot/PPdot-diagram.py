'''
Code Purpose: Makes a P-Pdot diagram by quering the ATNF pulsar catalogue. 
Author: Owen A. Johnson
Date: 12/01/2024
'''
#%%
import numpy as np 
import matplotlib.pyplot as plt
import scienceplots; plt.style.use(['science','ieee']); ibm_cols = ['#6490ff', '#795ef0', '#dc5880', '#fe6100', '#ffae00']
import pandas as pd
from psrqpy import QueryATNF
from astropy.table import Table
import matplotlib.image as mpimg

query = QueryATNF(params=['NAME', 'RaJ', 'DecJ','P0', 'P1', 'ASSOC', 'BINARY', 'TYPE', 'MINMASS', 'DIST', 'PMTOT', 'VTRANS', 'ASSOC', 'PMRA', 'PMDEC', 'PB']) # Query the ATNF pulsar catalogue for the following parameters: P0, P1, BINARY, TYPE, P1_I

table = query.table.to_pandas() # The table of ATNF pulsars
print('Number of Pulsars in the ATNF Catalogue: ', len(table))


total_period = table['P0'].values # The total period of the pulsar
total_p1 = table['P1'].values # The total period derivative of the pulsar

# --- Selcting Black Widows --- 
BW_table = table[table['MINMASS'] < 0.05] # Selecting pulsar binaries with a minimum mass less than 0.1 solar masses)
BW_table = BW_table[BW_table['P0'] < 0.01] # Selecting pulsar with a rotational period less than 1 second
BW_table = BW_table[BW_table['PB'] < 10/24] # Selecting pulsars with binary period less than 10 hours 
print('Number of Black Widow Pulsars in the ATNF Catalogue: ', len(BW_table))

# --- Selecting Redbacks ---
RB_table = table[table['MINMASS'] > 0.2] # Selecting pulsar binaries with a minimum mass greater than 0.1 solar masses)
RB_table = RB_table[RB_table['P0'] < 0.01] # Selecting pulsars with a rotational period less than 1 ms
RB_table = RB_table[RB_table['PB'] < 1] # Selecting pulsars with binary period less than 1 day 
print('Number of Redback Pulsars in the ATNF Catalogue: ', len(RB_table))

# -- Selecting Single MSPs --- 
MSP_table = table[table['BINARY'].isna()]# Selecting pulsars that are not binary
MSP_table = MSP_table[MSP_table['P0'] < 0.01] # Selecting pulsars with a rotational period less than 0.01 second

plt.figure(figsize=(6,4)) # Set the figure size
plt.xlim(0.001, 20)
plt.ylim(10**(-22), 10**(-9))

plt.scatter(BW_table['P0'], BW_table['P1'], s=4, c='blue', marker='D', label='Black Widows', zorder = 2, edgecolors='k', linewidth=0.5) 
plt.scatter(RB_table['P0'], RB_table['P1'], s=4, c='red', marker='s', label='Redbacks', zorder = 3, edgecolors='k', linewidth=0.5) 
plt.scatter(MSP_table['P0'], MSP_table['P1'], s=2, c='green', marker='o', label='Single MSPs', zorder = 1, alpha = 0.5) 

plt.scatter(total_period, total_p1, s=1, c='grey', marker='o', label='ATNF Pulsars', zorder = 0, alpha=0.5) # Plot the total period derivative against the total period
plt.scatter(0.0333924, 4.21*10**(-13), s=10, c=ibm_cols[1], marker='*', label='Crab', zorder = 4)

# --- Adding Extras --- 

x = np.linspace(0.001, 30, 1000) # The x-axis values for the lines

# - Death Line -  Chen & Ruderman 1993
plt.plot(x, 10**(-16.16)*(x**(2.75)), c='r', linestyle='--') # Plot the death line
plt.fill_between(x, 10**(-16.16)*(x**(2.75)), 10**(-30.5)*(x**(2.75)), color='r', alpha=0.2)

# - Ages - 
age_labels = ['1 kyr', '100 kyr', '10 Myr', '1 Gyr']
for i in range(11, 19, 2): 
    plt.plot(x,  (1.59*10**-i)*x, c='k', linestyle='-', alpha = 0.2) 
    plt.text(0.01, (12.5*10**-i)*0.002, age_labels[int((i-11)/2)], fontsize=8, rotation=10)

pow_labels = ['$10^{39}$ erg/s', '$10^{36}$ erg/s', '$10^{33}$ erg/s', '$10^{30}$ erg/s', '$10^{27}$ erg/s']
for i in range(8, 23, 3): 
    plt.plot(x, (2.536*10**-i)*x**3, c='k', linestyle='-.', alpha = 0.2)
    # skip the first one
    if i != 8:
        plt.text(2, (2000*10**-i)*0.002, pow_labels[int((i-8)/3)], fontsize=8, rotation=35)

# - Magnetic Field lines - 
B_labels = ['$10^{14}$ G', '$10^{12}$ G', '$10^{10}$ G', '$10^{8}$ G']
for i in range(12, 28, 4): 
    plt.plot(x, (9.76*10**-i)/x, c='k', linestyle='--', alpha = 0.2)
    plt.text(0.05, (0.25*10**-i)/0.002, B_labels[int((i-12)/4)], fontsize=8, rotation=-12, weight='bold')


plt.xscale('log') # Set the x-axis to a log scale
plt.yscale('log') # Set the y-axis to a log scale
plt.xlabel('Period, $P$ [s]') # Label the x-axis
plt.ylabel('Period Derivative, $\dot P$ [s$^{-1}]$') # Label the y-axis
plt.legend(loc='upper left', frameon=False, fontsize=8) # Add a legend to the plot
# custom xtick labels 
plt.xticks([0.001, 0.01, 0.1, 1, 10], ['1 ms', '10 ms', '100 ms', '1 s', '10 s'])

plt.savefig('PPdot-diagram.pdf', bbox_inches='tight') # Save the figure