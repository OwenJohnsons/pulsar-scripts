#!/usr/bin/env python3

import argparse
import os
import your
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FixedLocator
import scienceplots; plt.style.use(['science','ieee', 'no-latex'])
from tqdm import tqdm

def get_args():
    # --- Parser ---
    parser = argparse.ArgumentParser(description='Dynamic Spectra Plotter for LOFTS data.')
    parser.add_argument('-f', '--fil', type=str, help='Path of the filterbank file.', required = True)
    parser.add_argument('-c', '--colour', type=str, help='Waterfall colour, from matplotlib.', required = False, default='magma')
    return parser.parse_args()

def get_metadata(hdr):

    trgt = hdr.basename.split('.')[0]
    strt_date = hdr.tstart_utc
    
    # metadata += f"Path: {hdr.filename}\n"
    metadata += f"Target: {trgt}\n"
    metadata += f"Start Date: {strt_date}\n"
    metadata += f"Total Bandwidth (MHz): {hdr.nchans * abs(hdr.foff)}\n"
    metadata += f"Sample Rate (s): {hdr.tsamp}\n"
    metadata += f"Number of Channels: {hdr.nchans}\n"
    metadata += f"Number of Samples: {hdr.native_nspectra}\n"
    metadata += f"Channel Width (MHz): {abs(hdr.foff)}\n"
    metadata += f"Observation Length (mins): {(hdr.native_nspectra * hdr.tsamp)/60:.1f}\n"
    metadata += f"$t_0$ (s): {hdr.native_nspectra/2 * hdr.tsamp:.1f}\n"

    return metadata

def set_xticks(hdr, data_shape, nticks=8):
    top_freq = hdr.fch1
    bottom_freq = hdr.fch1 + (hdr.nchans - 1) * hdr.foff
    tick_positions = np.linspace(0, data_shape[1] - 1, nticks)
    xtick_vals = np.linspace(top_freq, bottom_freq, nticks)

    return xtick_vals, tick_positions

def set_yticks(hdr, data_shape, nend, nticks=8):
    duration = nend * hdr.tsamp
    ytick_pos = np.linspace(0, data_shape[0] - 1, nticks)
    ytick_vals = np.linspace(0, duration, nticks)

    return ytick_pos, ytick_vals

def obs_slice(hdr, len):
    nsamples = hdr.native_nspectra

    ctr_sample = int(nsamples/2)

    if len > nsamples:
        print(f"Requested length {len} exceeds available samples {nsamples}. Adjusting to maximum available samples.")
        return (0, nsamples)

    return (ctr_sample - len/2), (len)

def plot_wat_spectrum(fil_obj, hdr, save_path, args):

        nstrt, nend = obs_slice(hdr, 1000)
        fil_data = fil_obj.get_data(nstart=nstrt, nsamp=nend)
        print(fil_data.shape)

        spectrum = np.mean(fil_data, axis=0)
        print(spectrum.shape)

        # --- Plotting ---
        fig = plt.figure(figsize=(5, 4))

        gs = gridspec.GridSpec(2, 1, height_ratios=[1, 3], hspace=0)

        ax0 = plt.subplot(gs[0])
        ax1 = plt.subplot(gs[1], sharex=ax0)
        ax0.plot(spectrum, color='k', lw=1)
        ax0.set_yscale('log')
        ax0.tick_params(labelbottom=False)

        imshow_col = args.colour
        vmin, vmax = np.percentile(fil_data, [5, 95])
        ax1.imshow(fil_data, aspect='auto', cmap=imshow_col, origin='lower', vmin=vmin, vmax=vmax)

        xtick_vals, tick_positions = set_xticks(hdr, fil_data.shape)
        tick_labels = [str(int(round(val))) for val in xtick_vals]
        ax1.set_xticks(tick_positions); ax1.set_xticklabels(tick_labels)
        ax1.set_xlabel('Frequency [MHz]')

        ytick_pos, ytick_vals = set_yticks(hdr, fil_data.shape, nend)
        ax1.set_yticks(ytick_pos)
        ax1.set_yticklabels([f"{val:.1f}" for val in ytick_vals])
        ax1.set_ylabel('Time [s]')

        # --- Metadata ---
        metadata = get_metadata(hdr)
        ax0.text(0.5, 1.05, metadata, transform=ax0.transAxes, ha='left', va='bottom')

        # --- Save ---
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")

def main():
    args = get_args()

    # --- Loading filterbank data ---
    fil_path = args.fil
    station = args.station
    # fil_path = args['fil']
    # station = args['station']
    save_plt = fil_path.replace('.fil', '.png')

    header = your.Your(fil_path).your_header
    fil_obj = your.Your(fil_path)

    fil_basename = os.path.basename(fil_path)
    print('Plotting %s' % fil_basename)
    
    plot_wat_spectrum(fil_obj, header, save_plt)

if __name__ == "__main__":
    main()