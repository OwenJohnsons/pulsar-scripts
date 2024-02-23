#%% 
'''
Purpose: Read the Raw output from ACCEL_sift.py (PRESTO) and generate a .csv file with the candidates and their properties along with a .txt file with the prepfold commands for the candidates.
Author: Owen A. Johnson 
Date: 2024-02-22
'''

import numpy as np 
import matplotlib.pyplot as plt
import smplotlib
import glob
import re
import pandas as pd

file_list = glob.glob('sift*.txt')

cand_num = []; file_names = []
cand_dms = []; cand_snrs = []; cand_sigmas = []
num_harm = []; ipow = []; cpow = []; Period = []
r = []; z = []; num_hits = [] 

for file in file_list:
    with open(file) as f:
        for line in f:
            if 'uwl' in line:
                header = line.split(':')[1]; obs_file_name = line.split(':')[0]
                numbers = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', header)
                numbers = [float(num) if '.' in num else int(num) for num in numbers]

                # appending to lists
                cand_num.append(numbers[0])
                cand_dms.append(numbers[1]) 
                cand_snrs.append(numbers[2])
                cand_sigmas.append(numbers[3])  
                num_harm.append(numbers[4])
                ipow.append(numbers[5])
                cpow.append(numbers[6])
                Period.append(numbers[7])
                r.append(numbers[8])
                z.append(numbers[9])
                num_hits.append(numbers[10])
                file_names.append(obs_file_name)   

            if 'DM=' in line:
                line = line.replace(" ", "")
                parts = line.split('=')
            
                dm = re.sub(r'[^0-9.]', '', parts[1])
                snr = re.sub(r'[^0-9.]', '', parts[2])
                sigma = re.sub(r'[^0-9.]', '', parts[3])


        dataframe = pd.DataFrame({'file': file_names,'cand_num':cand_num, 'DM': cand_dms, 'SNR': cand_snrs, 'Sigma': cand_sigmas, 'numharm': num_harm, 'ipow': ipow, 'cpow': cpow, 'P(ms)': Period, 'r': r, 'z': z, 'numhits': num_hits})
        print('Number of candidates pre-filter:', len(dataframe))

        # filtering the dataframe
        dataframe = dataframe[dataframe['Sigma'] > 8]
        dataframe = dataframe.sort_values(by='Sigma', ascending=False)
    
        print('Number of candidates:', len(dataframe))
        dataframe.to_csv('%s.csv' % file.split('.')[0], index=False)

        # generate prepfold commands to .txt file
        with open("%s_commands.txt"  % file.split('.')[0], "w") as file:
            # generate prepfold commands to .txt file
            for i in range(len(dataframe)):
                command = f'prepfold -nsub 3328 -p {dataframe.iloc[i]["P(ms)"]/1000} -dm {dataframe.iloc[i]["DM"]} {dataframe.iloc[i]["file"].split("_prepsubband")[0]}.sf\n'
                file.write(command)

