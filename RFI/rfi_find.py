"""
Code Purpose: Perform rfifind (PRESTO, Ransom, 2018) on a given set of files on a specified directory, placing product outputs into seperate folders. 
Author: Owen Johnson.
Last Major Update: 14/12/2022
"""

import os 
import glob 
import argparse 

# - Command line arguments - 
parser = argparse.ArgumentParser(description='Performs rfi find on a given directory of valid psrfits files.')

parser.add_argument('-d', '--directory', type=str,  required= True, help='directory of psrfits files to be processed')
parser.add_argument('-o', '--output', type=str, required= False, help='output directory for rfi find products')
parser.add_argument('-b', '--blocks', type=float, required= True, help='rfifind block integration size')

args = parser.parse_args()

# - Main code -

# - Check if output directory exists, if not create it -
if args.output == None:
    args.output = args.directory + '/rfi_find'
    if not os.path.exists(args.output):
        os.mkdir(args.output)

# - Loading file locations - 
files = glob.glob(args.directory + '/*.sf')

print('\n --- \n Files found in directory: \n ---', len(files))

# - Looping through files and performing rfi find -

for file in files:
    print('Processing file: ', file)
    os.system('rfifind -blocks ' + str(args.blocks) + ' -o ' + args.output + '/' + file.split('/')[-1].split('.')[0] + ' ' + file)