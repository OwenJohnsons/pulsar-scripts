#%%
import argparse
import numpy as np
import matplotlib.pyplot as plt
import os
import scienceplots
import pandas as pd 
from glob import glob
# %matplotlib inline

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

def norm_x(val, ax):
    x_min, x_max = ax.get_xlim()
    return (val - x_min) / (x_max - x_min)

def plot_phase_space(args):
    # Set up the plot
    fig, ax1 = plt.subplots(figsize=(8, 6), dpi=200)

    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel(r'$\nu W$ (GHz s)')
    ax1.set_ylabel(r'$L_{\nu}$ (Jy kpc$^2$)')
    ax1.set_xlim(1.0e-10, 1.0e+10)
    ax1.set_ylim(1.0e-12, 1.0e+16)

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
    ax1.fill_between(x, L(1e12, x), 1e-12, color='#118ab2', alpha=0.1)
    ax1.text(1e4, 1e1, "$\\textbf{Incoherent Emission}$", rotation=50, fontsize=10, color='#118ab2')
    ax1.text(1e3, 1e2, "$\\textbf{Coherent Emission}$", rotation=50, fontsize=10, color='#073b4c')

    # Uncertainty principle region 
    ax1.fill_betweenx([1.0e-12, 1.0e+16], 1.0e-10, 1.0e-9, color='#ae2012', alpha=0.3)
    ax1.text(2e-10, 1e-1, "Uncertainty Principle", rotation=90, fontsize=10, color='#ae2012')
    ax1.axvline(1.0e-9, color='black', linestyle='-')
    
    colors = [
    "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2",
    "#D55E00", "#CC79A7", "#999999", "#117733", "#88CCEE",
    "#44AA99", "#DDCC77", "#882255", "#AA4499", "#332288",
    "#66CCEE", "#228833", "#CC6677", "#4477AA", "#EE7733",
    "#BBBBBB", "#76B7B2", "#E15759", "#4E79A7", "#59A14F",
    "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"]


    # Plot data
    data_files = {
    "psrs_2": {"color": "#CC6677", "label": "Pulsars", "cols": (4, 5), "marker": "o"},
    "rrats_nohead": {"color": "#88CCEE", "label": "RRATs", "cols": (4, 5), "marker": "p"},
    "frbs_vals_to_plot": {"color": "#EE7733", "label": "FRBs", "cols": (1, 0), "marker": "D"},
    "solar_vals": {"color": "#228833", "label": "Solar Bursts", "cols": (4, 5), "marker": "v"},
    "AGNs": {"color": "#E15759", "label": "AGNs", "cols": (0, 1), "marker": "o"},
    "FlareStars": {"color": "#F32424", "label": "Flare Stars", "cols": (0, 1), "marker": "^"},
    'Novae': {"color": "#332288", "label": "Novae", "cols": (0, 1), "marker": "o"},
    'GRBs': {"color": "#45CFDD", "label": "GRBs", "cols": (0, 1), "marker": "o"},  
    'SuperNova': {"color": "#FF06B7", "label": "Supernovae", "cols": (0, 1), "marker": "o"},
    'Xray': {"color": "#A0C334", "label": "X-ray Binaries", "cols": (0, 1), "marker": "x"},
    'RSCV': {"color": "#41B3A2", "label": "RS CVm \& Algol", "cols": (0, 1), "marker": "d"},
    'MCV': {"color": "#9C755F", "label": "Magnetic CVs", "cols": (0, 1), "marker": "8"},
    }   
    
    sources = [
    # Uranus Lightning
    {
        "name": "Uranus UED",
        "frequency": 1.5e7,
        "pulse_width": 0.12,
        "SEFD": 1e4,
        "distance_kpc": 0.00009,
        "sigma_threshold": 4
    },

    # Saturn Lightning
    {
        "name": "Saturn SED (Voyager)",
        "frequency": 2.0e7,
        "pulse_width": 0.05,
        "SEFD": 1e4,
        "distance_kpc": 0.00005,
        "sigma_threshold": 4
    },
    {
        "name": "Saturn SED (UTR-2)",
        "frequency": 2.0e7,
        "pulse_width": 0.05,
        "SEFD": 1e4,
        "distance_kpc": 0.00005,
        "sigma_threshold": 4
    }
    ]
    
    lpts = [

    # Long-Period Transients
    {
        "name": "LPT",
        "frequency": 1.1e8,
        "pulse_width": 45,
        "SEFD": 2000,
        "distance_kpc": 1.3,
        "sigma_threshold": 5
    },
    {
        "name": "LPT",
        "frequency": 1.1e8,
        "pulse_width": 150,
        "SEFD": 2000,
        "distance_kpc": 5.7,
        "sigma_threshold": 5
    },
    {
        "name": "LPT",
        "frequency": 8.875e8,
        "pulse_width": 30,
        "SEFD": 1000,
        "distance_kpc": 4.85,
        "sigma_threshold": 8
    },
    {
        "name": "LPT",
        "frequency": 6e8,
        "pulse_width": 120,
        "SEFD": 1000,
        "distance_kpc": 0.17,
        "sigma_threshold": 10
    },
    {
        "name": "LPT",
        "frequency": 3.3e8,
        "pulse_width": 600,
        "SEFD": 1000,
        "distance_kpc": 8.0,
        "sigma_threshold": 6
    }
    ]
    
    # --- LPTs ---
    lpts = []
    for params in [
        (1.1e8,   45,   2000, 1.3,  5),
        (1.1e8,  150,   2000, 5.7,  5),
        (8.875e8, 30,   1000, 4.85, 8),
        (6e8,    120,   1000, 0.17, 10),
        (3.3e8,  600,   1000, 8.0,  6),
    ]:
        lpts.append({
            "name": "LPT",
            "frequency": params[0],
            "pulse_width": params[1],
            "SEFD": params[2],
            "distance_kpc": params[3],
            "sigma_threshold": params[4]
        })

    # Plot all LPTs with same color and label only once
    label_plotted = False
    for src in lpts:
        luminosity, nuW = calculate_luminosity_and_nuW(
            src["frequency"],
            src["pulse_width"],
            src["SEFD"],
            src["distance_kpc"],
            src["sigma_threshold"]
        )
        ax1.scatter(
            nuW,
            luminosity,
            s=5,
            color='purple',
            zorder=5,
            label='LPTs' if not label_plotted else None
        )
        label_plotted = True

    

    for filename, props in data_files.items():
        file_path = os.path.join('./gach_rud/', filename)
        if os.path.exists(file_path):
            data = np.loadtxt(file_path, usecols=props["cols"], dtype=float)  # Adjust columns as needed
            ax1.scatter(data[:, 0], data[:, 1], label=props["label"], color=props["color"], marker=props["marker"], s=8, zorder=3)

    # --- Manual Plotting --- 
    ax1.scatter(4e-3, 5e-9, s=8, label='Jupiter DAM')
    ax1.scatter(0.00000001,	4000, s=8, label='Crab Nano-shots')
    ax1.scatter(8.38e-4, 1.12e8, s=24, label='Galactic Magnetar (FRB 200428)', marker='*', color='purple', zorder=6)
    
    aukpc = 4.8481e-09 # 1 au in kpc
    jy = 1e-26 # 1 Jy in W/m^2/Hz
    uranus_ukr = (6.54e-21 / jy)*(aukpc**2)
    saturn_skr = (2.5e-19 / jy)*(aukpc**2)
    neptune_nkr = (5.06e-21 / jy)*(aukpc**2)
    
    ax1.scatter(1.034e+01, uranus_ukr, s=8, linewidth=2, alpha=0.7, label='Uranus (UKR)', color='cyan', zorder=3)
    ax1.scatter(5.136e+00, saturn_skr, s=8, linewidth=2, alpha=0.7, label='Saturn (SKR)', color='gold', zorder=3)
    ax1.scatter(4.833e+00, neptune_nkr, s=8, linewidth=2, alpha=0.7, label='Neptune (NKR)', color='blue', zorder=3)

    for src in sources:
        luminosity, nuW = calculate_luminosity_and_nuW(
            src["frequency"],
            src["pulse_width"],
            src["SEFD"],
            src["distance_kpc"],
            src["sigma_threshold"]
        )
        ax1.scatter(nuW, luminosity, s=5, label=src["name"], marker='h', zorder=5)

    handles, labels = ax1.get_legend_handles_labels()
    unique = dict()
    for h, l in zip(handles, labels):
        if l not in unique:
            unique[l] = h
    ax1.legend(unique.values(), unique.keys(), bbox_to_anchor=(1.1, 1), loc='upper left')
    

    # GRB data 
    # grb_data = np.loadtxt('./gach_rud/Gosia_GRB', usecols=(2, 7, 9))
    # grb_x = grb_data[:, 0]

    # Plot LFT3 sensitivity curves
    df = pd.concat((pd.read_csv(csv) for csv in glob("*.csv")), ignore_index=True)

    print(df.head())
    
    column_names = ['Frequency', 'SEFD']
    SEFD_low_values = df.sort_values(by=df.columns[0], ascending=True, ignore_index=True)
    SEFD_low_values.columns = column_names

    low_frequencies = SEFD_low_values['Frequency']*1e6; low_SEFD = SEFD_low_values['SEFD']
    # ------------------------------------------------------------
    # Sensitivity calculations
    # ------------------------------------------------------------

    distances = {
        "1 AU": 4.8481e-6,
        "0.1 kpc": 0.1,
        "100 kpc": 100,
    }

    durations = {
        "1 ms": 1e-3,
        "10 ms": 10e-3,
        "10 s": 10,
    }

    luminosity = {}
    nuW = {}

    for d_name, distance in distances.items():
        for t_name, duration in durations.items():

            lum, nu = calculate_luminosity_and_nuW(
                low_frequencies,
                duration,
                low_SEFD,
                distance,
                5,
            )

            luminosity[(d_name, t_name)] = lum
            nuW[(d_name, t_name)] = nu
        
    show_sens = True 


    if show_sens:

        colours = {
        "1 AU": "magenta",
        "0.1 kpc": "dodgerblue",
        "100 kpc": "firebrick",
        }
            
        hatches = {
        "1 ms": "..",
        "10 ms": "+",
        "10 s": "\\\\",}

        for distance in distances:      # Uses the actual dictionary keys
            for duration in durations:  # Uses the actual dictionary keys

                ax1.fill_between(
                    nuW[(distance, duration)],
                    luminosity[(distance, duration)],
                    ax1.get_ylim()[1],
                    color=colours[distance],
                    hatch=hatches[duration],
                    alpha=0.3,
                    label=f"{duration}, $5\\sigma$, {distance}",
                )
            
        

        


    # plot legend
    # ax1.legend(loc='lower right', fontsize=10, frameon=True)
    ax1.legend(bbox_to_anchor=(1.1, 1), loc='upper left', fontsize=8, markerscale=3)


    # Save plot
    if args.ps_output:
        plt.savefig('phase_space.ps')
    if args.png_output:
        plt.savefig('phase_space.pdf')

    # Show plot
    plt.savefig('phase_space_1.pdf')
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
