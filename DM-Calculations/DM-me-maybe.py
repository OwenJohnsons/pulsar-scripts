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
    parser.add_argument('-f0', type=float, required=True, help='Starting frequency in MHz')
    parser.add_argument('-f1', type=float, required=True, help='Ending frequency in MHz')
    parser.add_argument('-dt', type=float, required=True, help='Time resolution in ms')
    parser.add_argument('-nsub', type=int, default=32, help='Number of sub-bands')
    parser.add_argument('-df', type=float, required=True, help='Frequency resolution in MHz')
    parser.add_argument('-dmin', type=float, default=0.0, help='Minimum DM to consider')
    parser.add_argument('-dmax', type=float, required=True, help='Maximum DM to consider')
    parser.add_argument('-eff', type=float, default=5.0, help='SNR efficiency factor')
    parser.add_argument('-p', action='store_true', help='Makes Plots')
    parser.add_argument('-atnf', action='store_true', help='Includes ATNF benchmark lines in plots')
    parser.add_argument('-s', action='store_true', help='Save plots to file')
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

def tBW_smear(delta_DM_sub, f_low, f_high):
    """
    Calculate smearing from trial DM spacing across the full band .

    Parameters:
    delta_DM_sub : float
        DM trial step size (ΔDM) in pc cm^-3.
    f_low : float
        Band lower edge frequency in MHz.
    f_high : float
        Band upper edge frequency in MHz.

    Returns:
    t_bw_s : float
        Residual smearing time in seconds, assuming worst-case DM error ΔDM/2.
    """
    dm_err = 0.5 * float(delta_DM_sub)
    return dmdelay_exact(dm_err, f_high, f_low)

def _uniform_edges(f_low, f_high, n):
    """
    Build uniform subband edges across a frequency range.

    Parameters:
    f_low : float
        Band lower edge frequency in MHz.
    f_high : float
        Band upper edge frequency in MHz.
    n : int
        Number of subbands.

    Returns:
    edges : ndarray, shape (n, 2)
        Array of (f_low_edge, f_high_edge) in MHz for each subband.
    """
    f_low = float(f_low); f_high = float(f_high)
    n     = int(n)
    df    = (f_high - f_low) / n
    fl    = f_low + df * np.arange(n)
    fh    = fl + df
    return np.stack([fl, fh], axis=1)

def tSB_smear(delta_DM_sub, f_low, f_high, Nsub):
    """
    Calculate subband smearing from ΔDM within each subband .

    Parameters:
    delta_DM_sub : float
        DM trial step size (ΔDM) in pc cm^-3.
    f_low : float
        Band lower edge frequency in MHz.
    f_high : float
        Band upper edge frequency in MHz.
    Nsub : int
        Number of subbands.

    Returns:
    t_sb_s : float
        Worst-case (maximum across subbands) subband smearing time in seconds.
    """
    dm_err = 0.5 * float(delta_DM_sub)
    edges  = _uniform_edges(f_low, f_high, Nsub)  # (NNsub, 2)
    smears = dmdelay_exact(dm_err, edges[:, 1], edges[:, 0])
    return float(np.max(smears))

def total_smear(dt, t_ch_smear, t_sb_smear, t_bw_smear):
    """
    Compute total smearing as a quadrature sum (seconds).

    Parameters:
    dt : float 
        Sampling time in milliseconds.
    t_chan_smear : float
        Intra-channel smearing time in seconds.
    t_subband_smear : float
        Subband smearing time in seconds.
    t_bw_smear : float
        Bandwidth smearing time in seconds.
        DM-step smearing time in seconds.

    Returns:
    t_tot_s : float or ndarray
        Total smearing time in seconds.
    """
    dt_s  = np.asarray(dt, dtype=float) * 1e-3
    terms = [np.asarray(t_ch_smear, dtype=float),
             np.asarray(t_sb_smear, dtype=float),
             np.asarray(t_bw_smear  , dtype=float)]
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

def optimize_ddm(dm_grid,
                       f_low_mhz: float,
                       f_high_mhz: float,
                       df_mhz: float,
                       DM_constant=DM_constant):
    """
    Compute ΔDM the band and channelization.

    Parameters
    ----------
    dm_grid : array-like
        Array of DMs (pc cm^-3) at which to evaluate ΔDM.
    f_low_mhz : float
        Band lower edge in MHz.
    f_high_mhz : float
        Band upper edge in MHz.
    df_mhz : float
        Channel width in MHz.
    DM_constant : float
        Dispersion constant.

    Returns
    -------
    ddm : ndarray
        ΔDM for each DM in dm_grid (pc cm^-3).
    """
    dm_grid = np.asarray(dm_grid, dtype=float)

    # Build per-channel edges across the band
    fl = np.arange(f_low_mhz, f_high_mhz, df_mhz)
    fh = np.clip(fl + df_mhz, None, f_high_mhz)
    valid = fh > fl
    fl, fh = fl[valid], fh[valid]

    # Worst intra-channel smear at each DM (seconds), using exact edges
    inv2_span = (fl**-2 - fh**-2)                            # per-channel f^-2 span
    t_chan_max_s = DM_constant * dm_grid[:, None] * inv2_span[None, :]
    t_chan_max_s = np.max(t_chan_max_s, axis=1)              # worst channel per DM

    # Full-band
    band_span_inv2 = (f_low_mhz**-2 - f_high_mhz**-2)

    ddm = (2.0 * t_chan_max_s) / (DM_constant * band_span_inv2)

    return ddm

def nearest_value(value, array): 
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def benchmark_ATNF():
    from psrqpy import QueryATNF
    from astropy.table import Table
    
    print("\n=== ATNF Catalog Statistics === ")
    
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

def magnitudes(arr, step=0.5):
    """
    Selects elements whenever the log10(value) decreases by more than `step`.
    E.g. step=0.5 means every half order of magnitude (~×3.16).
    """
    arr = np.array(arr)
    log_vals = np.log10(arr)
    result = [arr[0]]

    cur_val = log_vals[0] - step
    for val, logv in zip(arr[1:], log_vals[1:]):
        if logv <= cur_val:
            result.append(val)
            cur_val = logv - step

    return np.array(result)

def main(): 
    
    # === Debug Args === #
    # ftop = 1920 
    # flow = 960
    # dt = 0.016384*1e3 # ms 
    # df = 0.024 # MHz
    # bw = ftop - flow
    # maxDM = 500 # pc cm^-3
    # fctr = (ftop + flow) / 2
    # nsub = int(bw/df) 
    
    # === Parse Args === #
    args = get_args()
    ftop = args.f1
    flow = args.f0
    dt   = args.dt  # ms
    df   = args.df  # MHz
    bw = ftop - flow
    minDM= args.dmin  # pc cm^-3
    maxDM= args.dmax  # pc cm^-3
    fctr = (ftop + flow) / 2
    outname = f"ddm_plan_f{int(flow)}-{int(ftop)}_dt{dt}_df{df}_dm{int(maxDM)}"
    
    if args.nsub:
        nsub = int(bw/df)
    else:
        nsub = args.nsub
        
    dms = np.linspace(minDM, maxDM, 1000)
    ddms = optimize_ddm(dms, flow, ftop, df)  
    ndms = 1/ddms

    plan_lims = magnitudes(ndms, step=0.5)
    plan_idxs = [nearest_value(val, ndms) for val in plan_lims]
    
    print('=== De-Dispersion Planning ===')
    print("DM Range: %s - %s pc cm^-3" % (np.min(dms), np.max(dms)))
    print("Frequency Range: %s - %s MHz" % (flow, ftop))
    print("Channel Width: %s MHz" % df)
    print("Number of Subbands: %s" % nsub)
    print("Sampling Time: %s ms" % dt)  
    
    
    print("\n=== DM Trial Info ===")
    print(" DM (pc cm^-3) | ΔDM (pc cm^-3) |  Trials per ΔDM")
    print("---------------------------------------------------")
    for idx in plan_idxs:
        print(f" {dms[idx]:14.2f} | {ddms[idx]:14.4f} | {ndms[idx]:16.2f}")

    print("\n=== Suggested DM Plan ===")
    print(" DM Start (pc cm^-3) | DM Stop (pc cm^-3) | ΔDM (pc cm^-3) | Number of Trials")
    print("----------------------------------------------------------------------------")
    for i in range(len(plan_idxs)-1):
        start_idx = plan_idxs[i]
        stop_idx  = plan_idxs[i+1]
        dm_start  = dms[start_idx]
        dm_stop   = dms[stop_idx]
        delta_dm  = ddms[stop_idx]
        n_trials  = int(np.ceil((dm_stop - dm_start) / delta_dm))
        print(f" {dm_start:18.2f} | {dm_stop:17.2f} | {delta_dm:14.4f} | {n_trials:17d}")
        
        # if last segment, fill to maxDM
        if i == len(plan_idxs) - 2 and dm_stop < maxDM:
            stop_idx = len(dms) - 1
            dm_start = dm_stop
            dm_stop  = maxDM
            delta_dm = ddms[stop_idx]
            n_trials = int(np.ceil((dm_stop - dm_start) / delta_dm))
            print(f" {dm_start:18.2f} | {dm_stop:17.2f} | {delta_dm:14.3f} | {n_trials:17d}")

   
 

    # --- Build per-channel edges from df  ---
    # channel lower edges
    chan_fl = np.arange(flow, ftop, df) 
    chan_fh = np.clip(chan_fl + df, None, ftop)  # discard any zero-width tail channel
    valid = chan_fh > chan_fl
    chan_fl = chan_fl[valid]
    chan_fh = chan_fh[valid]

    # --- Smearing Terms ---
    chan_smear_mat_s = dmdelay_exact(dms[:, None], chan_fh[None, :], chan_fl[None, :])
    freq_smear_s = np.max(chan_smear_mat_s, axis=1)  # worst channel per DM (seconds)
    
    # Smear across the band (seconds)
    bw_smear_s = tBW_smear(ddms[1], flow, ftop)  # scalar seconds

    # Subband smear (seconds, worst subband)
    subband_smear_s = tSB_smear(ddms[1], flow, ftop, nsub) 

    # Total smearing (seconds)
    total_smear_s = total_smear(dt, freq_smear_s, subband_smear_s, bw_smear_s)

    # --- Scattering (seconds) ---
    dms_scatter = np.where(dms == 0, 0.1, dms) # avoid log10(0)
    scat_ctr_s    = scattering_s(dms_scatter,  fctr/1000.0)
    scat_fch1_s   = scattering_s(dms_scatter,  flow/1000.0)
    scat_fchend_s = scattering_s(dms_scatter,  ftop/1000.0)

    total_plus_scatter_s = np.sqrt(total_smear_s**2 + scat_ctr_s**2) # summating scattering
    

    if args.p: 
        plt.figure(figsize=(10, 6), dpi=100)

        # --- Convert for plotting (ms) ---
        freq_smear       = freq_smear_s       * 1e3
        bw_smear         = bw_smear_s         * 1e3
        subband_smear    = subband_smear_s    * 1e3
        scat_ctr         = scat_ctr_s         * 1e3
        scat_fch1        = scat_fch1_s        * 1e3
        scat_fchend      = scat_fchend_s      * 1e3


        if args.atnf:
            w10_mean, w10_1sigma, p0_mean, p0_1sigma = benchmark_ATNF()
            plt.axhline(y=w10_mean, color='red', linestyle='-', label='W10 Mean')
            plt.axhline(y=(w10_mean + 3*w10_1sigma), color='red', linestyle='--', label='W10 + 3$\\sigma$')

        # --- Plotting Scattering ---
        plt.plot(dms, scat_ctr,   label='Scattering (%s MHz)' % int(fctr), color='orange')
        plt.plot(dms, scat_fch1,  label='Scattering (%s MHz)' % int(flow), color='orange', linestyle='dotted')
        plt.plot(dms, scat_fchend,label='Scattering (%s MHz)' % int(ftop), color='orange', linestyle='dashed')

        plt.axhline(y=dt, color='purple', linestyle='-.', label='Sampling Time')
        
        # print dm and freq_smear every 100 dm 
        # print("\nDM (pc cm^-3) | Freq Smear (ms)")
        # for dm_val in np.arange(0, dms.max(), 10):
        #     closest_DMidx = nearest_value(dm_val, dms)
        #     print(f"{dms[closest_DMidx]:.1f}           | {freq_smear[closest_DMidx]:.3f}")
        
        # --- Plotting Smearing ---
        plt.plot(dms, freq_smear,                label='Frequency Channel Smearing', color='blue')
        plt.plot(dms, bw_smear * np.ones_like(dms),    label='DM Step Smearing',      color='lime')
        plt.plot(dms, subband_smear * np.ones_like(dms), label='Subband Smearing',    color='green')
        plt.plot(dms, total_plus_scatter_s * 1e3, label='Total Smearing',           color='black', linestyle='--')

        # --- Plot Setup --- 
        plt.xlabel('DM (pc cm$^{-3}$)', fontsize=14); plt.xlim(dms[0], dms[-1])
        plt.ylabel('Smearing Time (ms)', fontsize=14)
        plt.yscale('log')
        plt.xlim(dms.min(), dms.max())
        plt.legend(frameon=True, fontsize=8, loc='lower right')
        plt.grid(True, ls='--', alpha=0.5)
        
        if args.s:
            plt.savefig(f"{outname}.png", dpi=300)
        plt.show()
        
        # --- Plotting DM Trials ---
        plt.figure(figsize=(10, 6), dpi=100)
        
        ax1 = plt.gca()
        ax1.plot(dms[1:], ndms[1:], color='red')
        ax1.set_yscale('log')
        ax1.set_xlabel('DM (pc cm$^{-3}$)')
        ax1.set_ylabel('Number of DM Trials per pc cm$^{-3}$', color='red')
        ax1.tick_params(axis='y', labelcolor='red')
        ax1.set_xlim(dms[0], dms[-1])

        ax2 = ax1.twinx()
        ax2.plot(dms[1:], ddms[1:])
        ax2.set_yscale('log')
        ax2.set_ylabel('$\Delta$ DM (pc cm$^{-3}$)', color ='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        plt.xlim(dms[0], dms[-1])
        plt.grid(True, ls='--', alpha=0.5)
        plt.show()

if __name__ == '__main__': 
    main()
# %%
