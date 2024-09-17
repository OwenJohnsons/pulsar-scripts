#%%
import argparse
import numpy as np
import matplotlib.pyplot as plt
import os
import scienceplots
import pandas as pd 

plt.style.use('science')

def calculate_luminosity_and_nuW(frequency, pulse_width, SEFD, distance_kpc, sigma_threshold):
    """
    Calculate the luminosity (Jy kpc^2) and nu W (GHz s).

    Parameters:
    - frequency (Hz): The frequency (or bandwidth) in Hz.
    - pulse_width (s): The pulse width in seconds.
    - SEFD (Jy): System Equivalent Flux Density in Jy.
    - distance_kpc (kpc): The distance to the source in kiloparsecs.
    - sigma_threshold (float): The threshold for the signal-to-noise ratio.

    Returns:
    - luminosity (Jy kpc^2): The spectral luminosity at the given distance.
    - nuW (GHz s): The product of frequency (in GHz) and pulse width.
    """
    
    # Convert frequency to GHz
    frequency_ghz = frequency * 1e-9
    
    # Calculate nu W (in GHz s)
    nu_W = frequency_ghz * pulse_width
    
    # Calculate flux density (assumed to be SEFD in this context)
    flux_density = SEFD / np.sqrt(frequency * pulse_width)
    flux_density = flux_density * sigma_threshold

    # Calculate luminosity
    luminosity = 4 * np.pi * (distance_kpc ** 2) * flux_density
    
    return luminosity, nu_W


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
        "rrats_nohead": {"color": "#06d6a0", "label": "RRATs", "cols": (4, 5)},
        "frbs_vals_to_plot": {"color": "#FF885B", "label": "FRBs", "cols": (1, 0)},
        "solar_vals": {"color": "#FF9F29", "label": "Solar Bursts", "cols": (4, 5)},
        "AGNs": {"color": "pink", "label": "AGNs", "cols": (0, 1)},
        "FlareStars": {"color": "#F32424", "label": "Flare Stars", "cols": (0, 1)},
        'Novae': {"color": "#693C72", "label": "Novae", "cols": (0, 1)},
        'GRBs': {"color": "#45CFDD", "label": "GRBs", "cols": (0, 1)},  
        'SuperNova': {"color": "#FF06B7", "label": "Supernovae", "cols": (0, 1)},
        'Xray': {"color": "#A0C334", "label": "X-ray Binaries", "cols": (0, 1)},
        'RSCV': {"color": "#41B3A2", "label": "RS CVm \& Algol", "cols": (0, 1)},
        'MCV': {"color": "#1F441E", "label": "Magnetic CVs", "cols": (0, 1)},
    }

    for filename, props in data_files.items():
        file_path = os.path.join('./gach_rud/', filename)
        if os.path.exists(file_path):
            data = np.loadtxt(file_path, usecols=props["cols"], dtype=float)  # Adjust columns as needed
            ax1.scatter(data[:, 0], data[:, 1], label=props["label"], color=props["color"], s=5, zorder=3)

    ax1.scatter(4e-3, 5e-9, s=5, label='Jupiter DAM')
    ax1.scatter(0.00000001,	4000, s=5, label='Crab Nano-shots')

    # GRB data 
    # grb_data = np.loadtxt('./gach_rud/Gosia_GRB', usecols=(2, 7, 9))
    # grb_x = grb_data[:, 0]

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
    ax1.legend(loc='lower right', fontsize=4, frameon=True)

    # Save plot
    if args.ps_output:
        plt.savefig('phase_space.ps')
    if args.png_output:
        plt.savefig('phase_space.png')

    # Show plot
   
    plt.show()

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