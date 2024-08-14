#%% 
from glob import glob
import re 
import matplotlib.pyplot as plt
import numpy as np
import scienceplots; plt.style.use('science')

file_list = glob('./*/*ACCEL_0')
print('Number of ACCEL_0 files at 0 DM:', len(file_list))

def read_file_ACCEL(file): 

    index = []; summed_pwr = []; coherent_pwr = []; period = []; frequency = []; period = []

    with open(file, 'r') as f:
        lines = f.readlines()

    for i in range(0, len(lines)): 
        if i > 2: 
            data_list = lines[i].split("  ")
            filtered_data_list = [entry for entry in data_list if entry.strip()]
            cleaned_data_list = [re.sub(r'\(\d+\)', '', entry).strip() for entry in filtered_data_list]

            print(cleaned_data_list)

            if cleaned_data_list == []: 
                break
            
            else: 
                index.append(int(cleaned_data_list[0]))
                summed_pwr.append(float(cleaned_data_list[2]))
                coherent_pwr.append(float(cleaned_data_list[3]))
                period.append((cleaned_data_list[5]))
                frequency.append(float(cleaned_data_list[6]))

        else: 
            continue

    return index, summed_pwr, coherent_pwr, period, frequency

total_index = []; total_summed_pwr = []; total_coherent_pwr = []; total_period = []; total_frequency = []

for file in file_list:
    index, summed_pwr, coherent_pwr, period, frequency = read_file_ACCEL(file)
    total_index.append(index)
    total_summed_pwr.append(summed_pwr)
    total_coherent_pwr.append(coherent_pwr)
    total_period.append(period)
    total_frequency.append(frequency)

flatten_summed_pwr = np.array([item for sublist in total_summed_pwr for item in sublist])

mask50 = flatten_summed_pwr < 50 
summed_pwr_50 = flatten_summed_pwr[mask50]

mask500 = flatten_summed_pwr < 500
summed_pwr_500 = flatten_summed_pwr[mask500]

plt.figure(figsize=(10, 5), dpi=200)
plt.hist(flatten_summed_pwr, bins=100, color='black', alpha=0.7, facecolor='None', edgecolor='black', linewidth=1, label='Summed Power < 500')
plt.xlabel('Summed Power')
plt.ylabel('Occurrence')
# plt.xscale('log')
plt.yscale('log')

