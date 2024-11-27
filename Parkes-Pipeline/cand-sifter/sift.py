#%% 
'''
Purpose: Read the Raw output from ACCEL_sift.py (PRESTO) and generate a .csv file with the candidates and their properties along with a .txt file with the prepfold commands for the candidates.
Author: Owen A. Johnson 
Date: 2024-02-22
'''

import numpy as np 
import matplotlib.pyplot as plt
import matplotlib as mpl
import glob
import re
import pandas as pd
import os 
import argparse 

file_list = glob.glob('/fred/oz203/data/PX094/J0523-2529/cand_plot/accelsearchcands/sifted/uwl*.txt')
sf_path = '/fred/oz203/data/PX094/J0523-2529/frequency_split'
sf_files = glob.glob(f'{sf_path}/*/*.sf')
output_file_path = "/fred/oz203/data/PX094/J0523-2529/cand_plot/accelsearchcands/sifted/prepfold_commands.txt"
ps_output_path = "/fred/oz203/data/PX094/J0523-2529/cand_plot/accelsearchcands/prepfold"

cand_num = []; file_names = []
cand_dms = []; cand_snrs = []; cand_sigmas = []
num_harm = []; ipow = []; cpow = []; Period = []
r = []; z = []; num_hits = [] 

master_dataframe = pd.DataFrame(columns=['file', 'cand_num', 'DM', 'SNR', 'Sigma', 'numharm', 'ipow', 'cpow', 'P(ms)', 'r', 'z', 'numhits'])

for file in file_list:
    with open(file) as f:
        for line in f:
            if 'uwl' in line:
                header = line.split(':')[1]
                obs_file_name = line.split(':')[0]
                numbers = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', header)
                numbers = [float(num) if '.' in num else int(num) for num in numbers]

                # Appending to lists
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

        # Create a dataframe for the current file
        dataframe = pd.DataFrame({
            'file': file_names,
            'cand_num': cand_num,
            'DM': cand_dms,
            'SNR': cand_snrs,
            'Sigma': cand_sigmas,
            'numharm': num_harm,
            'ipow': ipow,
            'cpow': cpow,
            'P(ms)': Period,
            'r': r,
            'z': z,
            'numhits': num_hits
        })

        dataframe = dataframe.sort_values(by='Sigma', ascending=False)

        # Print filtered stats
        # print(f'Number of candidates in {file}:', len(dataframe))
        dataframe.to_csv(f'{file.split(".")[0]}.csv', index=False)

        # Append to the master dataframe
        master_dataframe = pd.concat([master_dataframe, dataframe], ignore_index=True)



# filter based on SNR 
master_dataframe = master_dataframe.drop_duplicates(subset=['file', 'DM', 'SNR'], keep='first')
prepfold_df = master_dataframe[master_dataframe['SNR'] > 20]
print('Number of candidate commands generate for prepfold: %s' % len(prepfold_df))
# Save the overall dataframe to a CSV file
prepfold_df.to_csv('overall_candidates_huh.csv', index=False)


with open(output_file_path, 'w') as file:
    # generate prepfold commands to .txt file
    for i in (range(len(prepfold_df))):
        file_name = prepfold_df.iloc[i]["file"].split("_prepsub")[0]
        sf_file = [sf for sf in sf_files if file_name in sf][0]
        mask_file = os.path.join(os.path.dirname(sf_file), 'masks', f'{file_name}_rfifind.mask')
        ignore_chans = "0:115,216:335,402,485:563,575,578,582,664:743,778:809,812:895,958:991,996:1024,1252:1259,1276:1283,1292,1296,1300:1307,1316,1348,1432,1456,1472,1501:1504,1508,1511:1530,1596,1600,1668,1724,1735:1737,1784,1788,2084:2103,2784,3176:3179,3183:3184,3656:3689,4024:4128,4164:4203,4404:4483,4564:4643,4704:4799,4864,5079:5147,5312:5315,5436:5439,5492:5495,5500:5503,5556:5559,5624:5663,5684:5703,5744:5803,5824:5827,5844:5863,5948:5951,6004:6007,6012:6015,6068:6071,6089:6090,6392:6711,7132:7167,7384:7463,7864:7943,9471,10964:11042,11384:11462"

        orbital_commands = f'-bin -pb 59454.432 -e 0.04 -To 56577.14636 -w 0'
        # output_ps = (prepfold_df.iloc[i]["file"].split("_ACCEL")[0] + f'_SNR{prepfold_df.iloc[i]["SNR"]}').replace(".", "_")
        root_name = prepfold_df.iloc[i]["file"].split(".add")[0]; snr=int(prepfold_df.iloc[i]["SNR"]); dm = int(prepfold_df.iloc[i]["DM"])
        output_ps = f'{root_name}_SNR{snr}_DM{dm}'
        output_prefix = os.path.join(ps_output_path, output_ps)
        command = f'cd {ps_output_path}; prepfold -noxwin {orbital_commands} -n 128 -p {prepfold_df.iloc[i]["P(ms)"]/1000} -dm {prepfold_df.iloc[i]["DM"]} -ndmfact 1 -dmstep 5 -o {output_ps} -mask {mask_file} -ignorechan {ignore_chans} {sf_file}\n'

        ps_file = f'{output_prefix}_{prepfold_df.iloc[i]["P(ms)"]:.2f}ms_Cand.pfd.ps'
        
        # if ps_file not in glob.glob(f'{ps_output_path}/*'):

        file.write(command)

# figsize = 6
# fontsize = 13

# figsize_single = [figsize, figsize * (np.sqrt(5)-1)/2]
# adjust_single = dict(left=0.12, bottom=0.15, right=0.95, top=0.95)

# figsize_double = [2*fss for fss in figsize_single]
# adjust_double = dict(left=0.08, bottom=0.10, right=0.98, top=0.95)

# plt.figure(figsize=(10, 6))
# sc = plt.scatter(prepfold_df['P(ms)'], prepfold_df['DM'], c=prepfold_df['SNR'], cmap='viridis', s=5, alpha=0.8)
# plt.colorbar(sc, label='SNR')
# plt.xlabel('P [ms]')
# plt.xscale('log')
# plt.ylabel('DM [pc cm$^-3$]')
# plt.savefig('overall_candidates.png')

        