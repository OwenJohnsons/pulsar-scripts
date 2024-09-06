#%%
import argparse
import numpy as np
import matplotlib.pyplot as plt
import os
import scienceplots
import pandas as pd 

plt.style.use('science')

def plot_phase_space(args):
    # Set up the plot
    fig, ax1 = plt.subplots(figsize=(8, 6), dpi=200)

    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel(r'$\nu W$ (GHz s)')
    ax1.set_ylabel(r'$L_{\nu}$ (Jy kpc$^2$)')
    ax1.set_xlim(1.0e-10, 1.0e+10)
    ax1.set_ylim(1.0e-10, 1.0e+16)

    # Add second y-axis
    ax2 = ax1.twinx()
    ax2.set_yscale('log')
    ax2.set_ylabel(r'$L_{\nu}$ (ergs s$^{-1}$ Hz$^{-1}$)')
    ax2.set_ylim(1.0e+10, 1.0e+36)

    # Example of adding a constant brightness temperature line
    def L(TB, x):
        return TB * 2.761 * 1.05025e-18 * x**2
    
    x = np.logspace(-9, 10, 500)
    if args.TB:
        for TB in [1e4, 1e8, 1e12, 1e16, 1e20, 1e24, 1e28, 1e32, 1e36, 1e40]:
            ax1.plot(x, L(TB, x), linestyle='--', color='gray')
    
    # Add labels for the brightness temperature lines
    ax1.text(1e4, 3e7, "$10^{16}$ K", fontsize=10, color='gray', rotation=50)
    ax1.text(1e3, 3e9, "$10^{20}$ K", fontsize=10, color='gray', rotation=50)
    ax1.text(1e2, 3e11, "$10^{24}$ K", fontsize=10, color='gray', rotation=50)
    ax1.text(1e1, 3e13, "$10^{28}$ K", fontsize=10, color='gray', rotation=50)

    # Incoherent emission region
    ax1.fill_between(x, L(1e12, x), 1e-10, color='#118ab2', alpha=0.1)
    ax1.text(1e4, 1e1, "$\\textbf{Incoherent Emission}$", rotation=50, fontsize=10, color='#118ab2')
    ax1.text(1e3, 1e2, "$\\textbf{Coherent Emission}$", rotation=50, fontsize=10, color='#073b4c')

    # Uncertainty principle region 
    ax1.fill_betweenx([1.0e-10, 1.0e+16], 1.0e-10, 1.0e-9, color='#ae2012', alpha=0.3)
    ax1.text(2e-10, 1e0, "Uncertainty Principle", rotation=90, fontsize=10, color='#ae2012')
    ax1.axvline(1.0e-9, color='black', linestyle='-')

    # Plot data
    data_files = {
        "psrs_2": {"color": "#ef476f", "label": "Pulsars", "cols": (4, 5)},
        # "crab_nanogiant": {"color": "red", "label": "Crab Nano-shots", "cols": (0, 1)},
        # "crab_GRP": {"color": "purple", "label": "Crab GRPs", "cols": (5, 4)},
        # "GRPs_vals": {"color": "cyan", "label": "GRPs", "cols": (7, 8)},
        "rrats_nohead": {"color": "#06d6a0", "label": "RRATs", "cols": (4, 5)},
        "frbs_vals_to_plot": {"color": "#f15bb5", "label": "FRBs", "cols": (1, 0)},
        "solar_vals": {"color": "#ffd166", "label": "Solar Bursts", "cols": (4, 5)},
        # "SGR1935+2154": {"color": "pink", "label": "SGR 1935+2154", "cols": (2, 1)},
        # "Gosia_flare_stars": {"color": "orange", "label": "Flare Stars", "cols": (1, 2)},
    }

    for filename, props in data_files.items():
        file_path = os.path.join('./gach_rud/', filename)
        if os.path.exists(file_path):
            data = np.loadtxt(file_path, usecols=props["cols"])  # Adjust columns as needed
            ax1.scatter(data[:, 0], data[:, 1], label=props["label"], color=props["color"], s=5, zorder=3)

    ax1.scatter(4e-3, 5e-9, s=5)

    # Plot LFT3 sensitivity curves

    column_names = ['Frequency', 'SEFD']
    SEFD_low_values = pd.read_csv('Low-SEFD-LFT3.csv')
    SEFD_low_values.columns = column_names
    SEFD_high_values = pd.read_csv('High-SEFD-LFT3.csv')
    SEFD_high_values.columns = column_names

    low_frequencies = SEFD_low_values['Frequency']*1e6; low_SEFD = SEFD_low_values['SEFD']
    low_luminosity10ms, low_nuW10ms = calculate_luminosity_and_nuW(low_frequencies, 10e-3, low_SEFD, 1, 5)
    low_luminosity1ms, low_nuW1ms = calculate_luminosity_and_nuW(low_frequencies, 1e-3, low_SEFD, 1, 5)
    low_luminsity0_1ms, low_nuW0_1ms = calculate_luminosity_and_nuW(low_frequencies, .1e-3, low_SEFD, 1, 5)


    # hashed line above which LFT3 is sensitive
  

    ax1.fill_between(low_nuW10ms, low_luminosity10ms, ax1.get_ylim()[1], color='blue', alpha=0.3, hatch='//', label='10 ms, $5\sigma$')
    ax1.fill_between(low_nuW1ms, low_luminosity1ms, ax1.get_ylim()[1], color='red', alpha=0.3, hatch='//', label='1 ms, $5\sigma$')
    ax1.fill_between(low_nuW0_1ms, low_luminsity0_1ms, ax1.get_ylim()[1], color='green', alpha=0.3, hatch='//', label='0.1 ms, $5\sigma$')

    # plot legend
    ax1.legend(loc='lower right', fontsize=8)

    # Save plot
    if args.ps_output:
        plt.savefig('phase_space.ps')
    if args.png_output:
        plt.savefig('phase_space.png')

    # Show plot
   
    plt.show()


def calculate_pulsar_search_sensitivity(SEFD, obs_time, bandwidth, frequency, npol=2):
    """
    Calculate the RMS noise level and Signal-to-Noise Ratio (S/N) for a pulsar search.

    Parameters:
    SEFD (float): System Equivalent Flux Density in Jy.
    obs_time (float): Observation time in seconds.
    bandwidth (float): Bandwidth in Hz.
    frequency (float): Observing frequency in MHz.
    npol (int): Number of polarizations (default is 2).

    Returns:
    dict: Dictionary containing 'sigma_rms' and 'S/N' for a hypothetical pulsar with a flux density of 1 mJy.
    """
    # Convert frequency from MHz to Hz
    frequency_hz = frequency * 1e6

    # Calculate sigma_rms
    sigma_rms = SEFD / np.sqrt(npol * obs_time * bandwidth)

    pulsar_flux_density = 1e-3  # in Jy

    # Calculate Signal-to-Noise Ratio (S/N)
    sn_ratio = pulsar_flux_density / sigma_rms

    return sigma_rms, sn_ratio

def main():
    # parser = argparse.ArgumentParser(description='Plot Radio Transient Phase Space')
    # parser.add_argument('-all', action='store_true', help='Plot everything')
    # parser.add_argument('-psr', action='store_true', help='Plot pulsars')
    # parser.add_argument('-rrat', action='store_true', help='Plot RRATs')
    # parser.add_argument('-frb', action='store_true', help='Plot fast radio bursts')
    # parser.add_argument('-sun', action='store_true', help='Plot solar bursts')
    # parser.add_argument('-slow', action='store_true', help='Plot all slow transients')
    # parser.add_argument('-TB', action='store_true', help='Plot brightness temperature lines')
    # parser.add_argument('-cryopaf', action='store_true', help='Plot Parkes CryoPAF sensitivity curves')
    # parser.add_argument('-ps_output', action='store_true', help='Output postscript file')
    # parser.add_argument('-png_output', action='store_true', help='Output PNG file')
    
    # args = parser.parse_args()
    args = argparse.Namespace(psr=True, ps_output=False, png_output=True, TB=True)

    plot_phase_space(args)


if __name__ == '__main__':
    main()
# %%
ß