#%%
''' 
Code Purpose: Calculate a Dedispersion plan for a given observational setup. 
Author: Owen A. Johnson 
Last Major Update: 2025-10-10

Requirements: 

Usage:

'''
import argparse
import numpy as np 
import matplotlib.pyplot as plt
import scienceplots; plt.style.use(['science', 'no-latex'])

DM_constant = 4.148064239e3  # MHz^2 pc^-1 cm^3 s

def get_args(): 
    
    parser = argparse.ArgumentParser(description="Calculate a Dedispersion plan for a given observational setup.")
    parser.add_argument('--f0', type=float, required=True, help='Starting frequency in MHz')
    parser.add_argument('--f1', type=float, required=True, help='Ending frequency in MHz')
    parser.add_argument('--dt', type=float, required=True, help='Time resolution in ms')
    parser.add_argument('--nsub', type=int, default=32, help='Number of sub-bands')
    parser.add_argument('--df', type=float, required=True, help='Frequency resolution in MHz')
    parser.add_argument('--dm_max', type=float, required=True, help='Maximum DM to consider')
    parser.add_argument('--eff', type=float, default=5.0, help='SNR efficiency factor')
    args = parser.parse_args()
    return args


def dmdelay_exact(DM, f_high_mhz, f_low_mhz):
    """
    Calculate the exact cold-plasma dispersion delay between two frequencies.

    Parameters:
    DM : float or array-like
        Dispersion Measure in pc cm^-3.
    f_high_mhz : float or array-like
        Upper frequency in MHz.
    f_low_mhz : float or array-like
        Lower frequency in MHz.

    Returns:
    delay_s : float or ndarray
        Delay in seconds by which a pulse at f_low_mhz lags f_high_mhz.
    """
    DM = np.asarray(DM, dtype=float)
    fh2 = np.asarray(f_high_mhz, dtype=float)**2
    fl2 = np.asarray(f_low_mhz,  dtype=float)**2
    return DM_constant * DM * (1.0/fl2 - 1.0/fh2)


def tCHAN_smear(DM, f_low_edge_mhz, f_high_edge_mhz):
    """
    Calculate intra-channel smearing using channel edges (wideband-safe).

    Parameters:
    DM : float or array-like
        Dispersion Measure in pc cm^-3.
    f_low_edge_mhz : float
        Channel lower edge frequency in MHz.
    f_high_edge_mhz : float
        Channel upper edge frequency in MHz.

    Returns:
    t_chan_s : float or ndarray
        Intra-channel smearing time in seconds.
    """
    return dmdelay_exact(DM, f_high_edge_mhz, f_low_edge_mhz)


def tBW_smear(delta_DM_sub, f_low_band_mhz, f_high_band_mhz):
    """
    Calculate smearing from trial DM spacing across the full band (wideband-safe).

    Parameters:
    delta_DM_sub : float
        DM trial step size (ΔDM) in pc cm^-3.
    f_low_band_mhz : float
        Band lower edge frequency in MHz.
    f_high_band_mhz : float
        Band upper edge frequency in MHz.

    Returns:
    t_bw_s : float
        Residual smearing time in seconds, assuming worst-case DM error ΔDM/2.
    """
    dm_err = 0.5 * float(delta_DM_sub)
    return dmdelay_exact(dm_err, f_high_band_mhz, f_low_band_mhz)


def _uniform_edges(f_low_mhz, f_high_mhz, n):
    """
    Build uniform subband edges across a frequency range.

    Parameters:
    f_low_mhz : float
        Band lower edge frequency in MHz.
    f_high_mhz : float
        Band upper edge frequency in MHz.
    n : int
        Number of subbands.

    Returns:
    edges : ndarray, shape (n, 2)
        Array of (f_low_edge, f_high_edge) in MHz for each subband.
    """
    f_low_mhz  = float(f_low_mhz); f_high_mhz = float(f_high_mhz)
    n          = int(n)
    df         = (f_high_mhz - f_low_mhz) / n
    fl         = f_low_mhz + df * np.arange(n)
    fh         = fl + df
    return np.stack([fl, fh], axis=1)


def tSB_smear(delta_DM_sub, f_low_band_mhz, f_high_band_mhz, N_sub):
    """
    Calculate subband smearing from ΔDM within each subband (wideband-safe).

    Parameters:
    delta_DM_sub : float
        DM trial step size (ΔDM) in pc cm^-3.
    f_low_band_mhz : float
        Band lower edge frequency in MHz.
    f_high_band_mhz : float
        Band upper edge frequency in MHz.
    N_sub : int
        Number of subbands.

    Returns:
    t_sb_s : float
        Worst-case (maximum across subbands) subband smearing time in seconds.
    """
    dm_err = 0.5 * float(delta_DM_sub)
    edges  = _uniform_edges(f_low_band_mhz, f_high_band_mhz, N_sub)  # (N_sub, 2)
    smears = dmdelay_exact(dm_err, edges[:, 1], edges[:, 0])
    return float(np.max(smears))


def total_smear(dt_ms, t_chan_s, t_subband_smear_s, t_bw_smear_s):
    """
    Compute total smearing as a quadrature sum (seconds).

    Parameters:
    dt_ms : float or array-like
        Sampling time in milliseconds.
    t_chan_s : float or array-like
        Intra-channel smearing time in seconds.
    t_subband_smear_s : float or array-like
        Subband smearing time in seconds.
    t_bw_smear_s : float or array-like
        DM-step smearing time in seconds.

    Returns:
    t_tot_s : float or ndarray
        Total smearing time in seconds.
    """
    dt_s  = np.asarray(dt_ms, dtype=float) * 1e-3
    terms = [np.asarray(t_chan_s, dtype=float),
             np.asarray(t_subband_smear_s, dtype=float),
             np.asarray(t_bw_smear_s, dtype=float)]
    acc = dt_s**2
    for t in terms:
        acc = acc + t**2
    return np.sqrt(acc)


def scattering_s(DM, f_GHz):
    """
    Calculate the scattering time based on DM and observing frequency.

    Parameters:
    DM : float or array-like
        Dispersion Measure in pc cm^-3.
    f_GHz : float or array-like
        Observing frequency in GHz.

    Returns:
    t_scatter_s : float or ndarray
        Scattering time in seconds (Bhat et al. 2004-style empirical fit).
    """
    DM = np.asarray(DM, dtype=float)
    log_t_us = -6.46 + 0.154*np.log10(DM) + 1.07*(np.log10(DM))**2 - 3.86*np.log10(f_GHz)
    return (10.0**log_t_us) * 1e-6


def scattering(DM, f_GHz):
    """
    Calculate the scattering time based on DM and observing frequency.

    Parameters:
    DM : float
        Dispersion Measure in pc cm^-3
    f_GHz : float
        Observing frequency in GHz

    Returns:
    t_scatter : float
        Scattering time in microseconds (μs)
    """
    log_t_scatter = -6.46 + 0.154 * np.log10(DM) + 1.07 * (np.log10(DM))**2 - 3.86 * np.log10(f_GHz)
    t_scatter = 10 ** log_t_scatter  # in microseconds
    return t_scatter

def nearest_value(value, array): 
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def benchmark_ATNF():
    from psrqpy import QueryATNF
    from astropy.table import Table
    
    print("=== ATNF Catalog Statistics === ")
    
    query = QueryATNF(params=['NAME', 'W50', 'W10', 'DM', 'P0'])
    table = query.table.to_pandas() # The table of ATNF pulsars
    
    widths_tbl = table.dropna(subset=['W10'])
    
    W10_mean = np.mean(widths_tbl['W10'])
    W10_1sigma = np.std(widths_tbl['W10'])
    
    print(f"Mean W10: {W10_mean:.2f} ms"
      f"\n1σ W10: {W10_1sigma:.2f} ms")
    
    period_tbl = table.dropna(subset=['P0'])
    period_tbl = period_tbl[period_tbl['P0'] > 0]  
    
    P0_mean = np.mean(period_tbl['P0'])
    P0_1sigma = np.std(period_tbl['P0'])
    
    print(f"Mean P0: {P0_mean:.2f} s"
      f"\n1σ P0: {P0_1sigma:.2f} s")

    return W10_mean, W10_1sigma, P0_mean, P0_1sigma


def main(): 
    
    plotting = True
    atnf = True
    
    # === Debug Args === #
    ftop = 190 
    flow = 110
    dt = 0.655 # ms 
    df = 0.195 # MHz
    bw = ftop - flow
    maxDM = 800 # pc cm^-3
    fctr = (ftop + flow) / 2
    nsub = 32 # number of subbands
    
    dms = np.linspace(0, 800, 100)
    
    if plotting: 
        plt.figure(figsize=(10, 8), dpi=150)

        # --- Build per-channel edges from df  ---
        # channel lower edges
        chan_fl = np.arange(flow, ftop, df) 
        chan_fh = np.clip(chan_fl + df, None, ftop) 
        # discard any zero-width tail channel
        valid = chan_fh > chan_fl
        chan_fl = chan_fl[valid]
        chan_fh = chan_fh[valid]

        # --- Smearing Terms ---
        chan_smear_mat_s = dmdelay_exact(dms[:, None], chan_fh[None, :], chan_fl[None, :])
        freq_smear_s = np.max(chan_smear_mat_s, axis=1)  # worst channel per DM (seconds)

        # Smear across the FULL band (seconds)
        bw_smear_s = tBW_smear(0.5, flow, ftop)  # scalar seconds

        # Subband smear (seconds, worst subband)
        subband_smear_s = tSB_smear(0.5, flow, ftop, nsub) 

        # Total smearing (seconds)
        total_smear_s = total_smear(dt, freq_smear_s, subband_smear_s, bw_smear_s)

        # --- Scattering (seconds) ---
        scat_ctr_s    = scattering_s(dms,  fctr/1000.0)
        scat_fch1_s   = scattering_s(dms,  flow/1000.0)
        scat_fchend_s = scattering_s(dms,  ftop/1000.0)

        # include scattering 
        total_plus_scatter_s = np.sqrt(total_smear_s**2 + scat_ctr_s**2)

        # --- Convert once for plotting (ms) ---
        freq_smear       = freq_smear_s       * 1e3
        bw_smear         = bw_smear_s         * 1e3
        subband_smear    = subband_smear_s    * 1e3
        total_smear_time = total_smear_s      * 1e3
        scat_ctr         = scat_ctr_s         * 1e3
        scat_fch1        = scat_fch1_s        * 1e3
        scat_fchend      = scat_fchend_s      * 1e3

        if atnf:
            w10_mean, w10_1sigma, p0_mean, p0_1sigma = benchmark_ATNF()
            plt.axhline(y=w10_mean, color='red', linestyle='-', label='W10 Mean')
            plt.axhline(y=(w10_mean + 3*w10_1sigma), color='red', linestyle='--', label='W10 + 3$\\sigma$')

        # --- Plotting Scattering ---
        plt.plot(dms, scat_ctr,   label='Scattering (150 MHz)', color='orange')
        plt.plot(dms, scat_fch1,  label='Scattering (190 MHz)', color='orange', linestyle='dotted')
        plt.plot(dms, scat_fchend,label='Scattering (110 MHz)', color='orange', linestyle='dashed')

        plt.axhline(y=dt*1000, color='purple', linestyle='-.', label='Sampling Time')

        # --- Plotting Smearing ---
        plt.plot(dms, freq_smear,                label='Frequency Channel Smearing', color='blue')
        plt.plot(dms, bw_smear * np.ones_like(dms),    label='DM Step Smearing',      color='lime')
        plt.plot(dms, subband_smear * np.ones_like(dms), label='Subband Smearing',    color='green')
        # plt.plot(dms, total_smear_time,          label='Total Smearing',              color='black', linestyle='--')
        plt.plot(dms, total_plus_scatter_s * 1e3, label='Total Smearing',           color='black', linestyle='--')

        # --- Plot Setup --- 
        plt.xlabel('DM (pc cm$^{-3}$)'); plt.xlim(dms[0], dms[-1])
        plt.ylabel('Smearing Time (ms)')
        plt.yscale('log')
        plt.legend(frameon=True, fontsize=8, loc='lower right')
        plt.grid(True, which='both', ls='--', alpha=0.5)

if __name__ == '__main__': 
    main()
# %%
