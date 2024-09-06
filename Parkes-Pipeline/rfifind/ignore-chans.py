'''
Code Purpose: Takes known RFI instances known for the UWL and compresses them into a single string of comma separated values or ranges for use with paz or presto. 
Author: Owen A. Johnson
'''

import numpy as np 

note, start_freq, end_freq = np.loadtxt('mask-frequencies.txt', unpack=True, delimiter='|', dtype=str)

print('Number of noted RFI instances:',  len(note))

freq_chans = np.linspace(704, 4032, 13312)
# convert start and end freq to float
start_freq = start_freq.astype(float); end_freq = end_freq.astype(float)

mask_array = [] 
for i in range(len(note)):
    start_freq[i] = float(start_freq[i])
    end_freq[i] = float(end_freq[i])

    mask = np.where((freq_chans >= start_freq[i]) & (freq_chans <= end_freq[i]))
    mask_array = np.append(mask_array, mask)

mask_array = mask_array.astype(int)
mask_array = np.unique(mask_array)
print('Percentage of always bad channels:', len(mask_array)/len(freq_chans)*100)

def compress_ranges(numbers):
    compressed = []
    start = numbers[0]
    for i in range(1, len(numbers)):
        if numbers[i] != numbers[i-1] + 1:
            if start == numbers[i-1]:
                compressed.append(str(start))
            else:
                compressed.append(f"{start}:{numbers[i-1]}")
            start = numbers[i]
    # Add the last range or number
    if start == numbers[-1]:
        compressed.append(str(start))
    else:
        compressed.append(f"{start}:{numbers[-1]}")
    
    return ','.join(compressed)

compressed_output = compress_ranges(mask_array)
# save the compressed output to a file  
with open('ignore-chans.txt', 'w') as f:
    f.write(compressed_output)

print('Compressed output saved to ignore-chans.txt')