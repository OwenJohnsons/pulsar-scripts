'''
Code Purpose: Single Pulse Analysis for PRESTO on UWL Data 
Author: Owen A. Johnson 
Date: 2025-02-11
'''
import argparse
import glob as glob
import os as os
import numpy as np 
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import scienceplots 
plt.style.use('science')

def fetch_args(): 
    '''
    Fetches the arguments from the command line 
    '''
    parser = argparse.ArgumentParser(description='Single Pulse Analysis for PRESTO on UWL Data')
    parser.add_argument('-i', '--input', type=str, help='Input directory', required=True)
    parser.add_argument('-t', '--threshold', type=float, help='Threshold for single pulse detection (default = 10)', required=False)
    parser.add_argument('-d', '--dm_trials', type=float, help='Number of DM trials (default = 1000)', required=False)
    
    return parser.parse_args()

def read_singlepulse(sp_file):
    '''
    Reads in a singlepulse file and returns the data as a numpy array
    '''
    dm, sig, time, sample, dfact = np.loadtxt(sp_file, skiprows=1, unpack=True)
    return dm, sig, time, sample, dfact

def expected_pulses(n_trials, snr_min, snr_max):
    """
    Computes the expected number of pulses between SNR_min and SNR_max
    assuming pure Gaussian noise.
    """
    prob_snr_min = 1 - stats.norm.cdf(snr_min)  # P(X ≥ snr_min)
    prob_snr_max = 1 - stats.norm.cdf(snr_max)  # P(X ≥ snr_max)
    
    expected_above_snr_min = prob_snr_min * n_trials
    expected_above_snr_max = prob_snr_max * n_trials
    
    expected_in_bin = expected_above_snr_min - expected_above_snr_max
    
    return expected_in_bin

def check_overmasking(t_obs, tsamp, dm, sig, time, dm_trials=1000, width_trials=8):
    """
    Checks for overmasking by comparing expected and observed pulses.
    """
    # Compute total number of statistical trials
    n_trials = (t_obs / tsamp) * dm_trials * width_trials

    print(f"Total statistical trials: {n_trials:.2e}")

    # SNR bins to analyze
    snr_bins = [(6.0, 6.5), (6.5, 7.0), (7.0, 7.5), (7.5, 8.0)]
    
    for snr_min, snr_max in snr_bins:
        expected_count = expected_pulses(n_trials, snr_min, snr_max)
        observed_count = np.sum((sig >= snr_min) & (sig < snr_max))
        
        print(f"SNR {snr_min} - {snr_max}: Expected {expected_count:.1f}, Observed {observed_count}")
        
        if observed_count < 0.5 * expected_count:
            print(f"⚠️ WARNING: Possible overmasking in {snr_min} - {snr_max} bin!")

    return

def marker_scaling(sig, threshold=10.0):
    """
    Scales the marker size based on S/N. Mimicing what is done by PRESTO in the same plot. 
    """
    min_size = 20; max_size = 1000 
        
    log_base = 30.0  # Higher values give a stronger effect
    marker_sizes = min_size + log_base * np.log1p(sig - threshold)
    
    return marker_sizes


    
    
def main():
    arguments = fetch_args()
     
    sp_files = glob.glob(os.path.join(arguments.input, '*.singlepulse'))
    
    # grab the header info from up a directory
    subband_name = os.path.basename(os.path.normpath(arguments.input))
    header = glob.glob(os.path.dirname(os.path.join(arguments.input)) + '/*%s.hdrinfo' % subband_name)[0]
    date, tobs, nchan, tsamp = np.loadtxt(header, usecols=(0, 1, 2, 3), dtype=str, skiprows=2)
    filename = np.loadtxt(header, usecols=(0), dtype=str)[0]
    
    print('\n-------------------')
    print('Filename: {}'.format(filename))
    print('Found {} singlepulse files'.format(len(sp_files)))
    
    # Concatenate the singlepulse files into a single array
    dm, sig, time, sample, dfact = [], [], [], [], []
    
    for sp_file in sp_files:
        dm_, sig_, time_, sample_, dfact_ = read_singlepulse(sp_file)
        dm = np.concatenate((dm, dm_))
        sig = np.concatenate((sig, sig_))
        time = np.concatenate((time, time_))
        sample = np.concatenate((sample, sample_))
        dfact = np.concatenate((dfact, dfact_))
        
    # if no single pulses are found, exit
    if len(dm) == 0:
        print('⚠️ No single pulses found in {} for current setup'.format(filename))
        return
    
    print('\n-------------------')
    print('Read in {} single pulses'.format(len(dm)))
    print('Average S/N: {}'.format(np.mean(sig)))
    print('\n-------------------\n')
    
    # Check for overmasking
    check_overmasking(float(tobs), float(tsamp), dm, sig, time)
    
    # Mask based on S/N threshold
    if arguments.threshold:
        mask = sig >= arguments.threshold
        dm = dm[mask]
        sig = sig[mask]
        time = time[mask]
        sample = sample[mask]
        dfact = dfact[mask]
        
        if len(dm) == 0:
            print('⚠️ No single pulses found in {} for current threshold'.format(filename))
            return
            
        print('\n-------------------')
        print('Masked based on S/N threshold of {}'.format(arguments.threshold))
        print('Remaining single pulses: {}'.format(len(dm)))
        print('Average S/N: {}'.format(np.mean(sig)))
        print('-------------------\n')
    
    # 3 square top plots, 1 bottom plot
    fig = plt.figure(figsize=(12, 8))
    gs = gridspec.GridSpec(2, 3, height_ratios=[1, 2])
    plt.suptitle('%s | S/N$_{thres}$ = %s | $N_{pulse} =$ %s' % (filename, arguments.threshold, len(dm)), fontsize=16)

    # Top row (3 plots)
    ax1 = plt.subplot(gs[0, 0])
    ax2 = plt.subplot(gs[0, 1])
    ax3 = plt.subplot(gs[0, 2])

    # Bottom row (1 plot spanning 3 columns)
    ax4 = plt.subplot(gs[1, :])

    # Histogram of S/N
    ax1.hist(sig, bins=100, color='black', histtype='step')
    ax1.set_xlabel('S/N')
    ax1.set_ylabel('Pulses')
    ax1.set_xlim(sig.min(), sig.max())

    # Histogram of DM
    ax2.hist(dm, bins=60, color='black', histtype='step')
    ax2.set_xlabel('DM (pc cm$^{-3}$)')
    ax2.set_ylabel('Pulses')
    ax2.set_xlim(0, dm.max())

    # DM vs. S/N scatter plot
    ax3.scatter(dm, sig, color='black', s=1)
    ax3.axhline(sig.mean(), color='red', linestyle='--')
    ax3.set_xlabel('DM (pc cm$^{-3}$)')
    ax3.set_ylabel('S/N')
    ax3.set_xlim(0, dm.max())
    ax3.set_ylim(sig.min(), sig.max())

    # Time vs. DM scatter plot spanning full bottom row
    marker_sizes = marker_scaling(sig, threshold=arguments.threshold)
    ax4.scatter(time, dm, s=marker_sizes, edgecolor='black', facecolor='none', alpha=0.3)
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('DM (pc cm$^{-3}$)')
    ax4.set_xlim(0, float(tobs))
    ax4.set_ylim(0, dm.max())

    # Adjust layout and save the figure
    plt.tight_layout()
    plt.savefig('singlepulse_analysis.png')
    output_file = os.path.join(arguments.input, f'{filename}_singlepulse_t{arguments.threshold}.png')
    plt.savefig(output_file)
    

if __name__ == '__main__':
    main()