#%%
import numpy as np 
import argparse 
import pygdsm

def find_nearest(array, value):
    """Find nearest value in an array."""
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def smin_sum(freq, T_sys, eta, A_phys, SNR_limit, T_obs,
                               chan_BW, dc=0.1, n_p=2, rfi_mask=None):
    """
    Compute S_min using the radiometer equation with optional RFI masking.

    Parameters:
    freq (numpy array): Frequency values in MHz.
    T_sys (numpy array): System temperature in K (same shape as freq).
    eta (numpy array): Aperture efficiency (same shape as freq).
    A_phys (float): Physical collecting area of the telescope in m².
    SNR_limit (float): Detection S/N threshold.
    T_obs (float): Observation time in seconds.
    chan_BW (float): Channel bandwidth in MHz.
    dc (float): Duty cycle factor (default 0.1).
    n_p (int): Number of polarizations summed.
    rfi_mask (numpy array or None): Boolean array (True = keep, False = RFI) of same length as freq.

    Returns:
    float: Minimum detectable flux density S_min in Jy.
    """

    
    k_B = 1380  
    chan_BW_Hz = chan_BW * 1e6  # Convert MHz to Hz

    duty_cycle = np.sqrt(dc / (1 - dc))

    # Apply RFI mask
    if rfi_mask is not None:
        freq = freq[rfi_mask]
        T_sys = T_sys[rfi_mask]
        eta = eta[rfi_mask]
    else:
        rfi_mask = np.ones_like(freq, dtype=bool)

    delta_f = np.full(len(freq), chan_BW)  
        
    S_min_per_freq = (T_sys * 2 * k_B) / (eta * A_phys) * \
                     (SNR_limit / np.sqrt(n_p * T_obs * chan_BW_Hz)) * \
                     duty_cycle 
                    
    
    S_min_sum = np.sum(S_min_per_freq * delta_f)
    effective_BW = np.sum(delta_f)
    print("Effective Bandwidth:", effective_BW)
    
    S_min_final = S_min_sum / (effective_BW) 

    return S_min_final * 1000  # Convert to mJy

def smin_total(freq, T_sys, eta, A_phys, SNR_limit, T_obs,
               chan_BW, dc=0.1, n_p=2, rfi_mask=None):
    """
    Compute the total minimum detectable flux density S_min over all channels using the radiometer equation.

    Parameters:
    freq (numpy array): Frequency values in MHz.
    T_sys (numpy array): System temperature in K (same shape as freq).
    eta (numpy array): Aperture efficiency (same shape as freq).
    A_phys (float): Physical collecting area of the telescope in m².
    SNR_limit (float): Detection S/N threshold.
    T_obs (float): Observation time in seconds.
    chan_BW (float): Channel bandwidth in MHz.
    dc (float): Duty cycle factor (default 0.1).
    n_p (int): Number of polarizations summed.
    rfi_mask (numpy array or None): Boolean array (True = keep, False = RFI) of same length as freq.

    Returns:
    float: Minimum detectable flux density S_min in mJy.
    """
    k_B = 1380  # Boltzmann constant in Jy m² / (K Hz)
    chan_BW_Hz = chan_BW * 1e6  # Convert MHz to Hz

    # Apply RFI mask
    if rfi_mask is not None:
        freq = freq[rfi_mask]
        T_sys = T_sys[rfi_mask]
        eta = eta[rfi_mask]

    # Effective (bandwidth-weighted) system parameters
    weights = np.ones_like(freq) * chan_BW
    T_sys_eff = np.average(T_sys, weights=weights)
    eta_eff = np.average(eta, weights=weights)

    # Total usable bandwidth
    total_BW_Hz = len(freq) * chan_BW_Hz
    duty_cycle_factor = np.sqrt(dc / (1 - dc))

    # over the full bandwidth
    S_min = (T_sys_eff * 2 * k_B) / (eta_eff * A_phys) * \
            (SNR_limit / np.sqrt(n_p * T_obs * total_BW_Hz)) * \
            duty_cycle_factor

    return S_min * 1000  # Convert to mJy

def smin_quadrature(freq, T_sys, eta, A_phys, SNR_limit, T_obs,
                    chan_BW, dc=0.1, n_p=2, rfi_mask=None):
    """
    Compute total S_min using quadrature sum over all frequency channels.

    This method accounts for different T_sys and eta per channel correctly.

    Returns:
        float: Total S_min in mJy.
    """
    k_B = 1380
    chan_BW_Hz = chan_BW * 1e6

    if rfi_mask is not None:
        freq = freq[rfi_mask]
        T_sys = T_sys[rfi_mask]
        eta = eta[rfi_mask]

    duty_cycle_factor = np.sqrt(dc / (1 - dc))

    # Compute per-channel S_min
    S_min_i = (T_sys * 2 * k_B) / (eta * A_phys) * \
              (SNR_limit / np.sqrt(n_p * T_obs * chan_BW_Hz)) * \
              duty_cycle_factor

    # Combine sensitivities in quadrature
    S_min_total = 1.0 / np.sqrt(np.sum(1.0 / S_min_i**2))

    return S_min_total * 1000  # Convert to mJy


def telescope_params(Tsys_file, ApEff_file):
    
    Tys_freq, Tsys = np.loadtxt(Tsys_file, unpack=True)
    ApEff_freq, ApEff = np.loadtxt(ApEff_file, unpack=True, delimiter=',')
    
    return Tys_freq, Tsys, ApEff_freq, ApEff


# def get_args():
#     parser = argparse.ArgumentParser(description="Calculate S_min using the radiometer equation.")
#     parser.add_argument("-fctr", "--freq", type=float, nargs='+', required=True, help="Frequency values in MHz (space-separated).")
#     parser.add_argument("-f1", "--f1", type=float, required=True, help="Start frequency in MHz.")
#     parser.add_argument("-f2", "--f2", type=float, required=True, help="End frequency in MHz.")
#     parser.add_argument("-tempfile", type=str, required=True, help="File containing rcvr temperature values in K.")
#     parser.add_argument("-etafile", type=str, required=True, help="File containing rcvr efficiency values (0-1) vs freq.")
#     parser.add_argument("-D", "--Dphys", type=float, required=True, help="Dish Diameter.")
#     parser.add_argument("-nchans", "--nchans", type=int, required=True, help="Number of channels.")
#     parser.add_argument("-SNR", default=7, type=float, help="SNR limit for detection (default: 7).")
#     parser.add_argument("-Tobs", "--Tobs", type=float, default=3600, help="Observation time in seconds (default: 3600).")
    
if __name__ == "__main__": 
    SNR_limit = 7.0  # SNR limit for detection
    T_obs = 3600.0  # Observation time in seconds    
    
    # Parkes Calculation 
    Tsys_file = "Parkes_Tsys.txt"
    ApEff_file = "UWL_AprEFF.txt"
    Tsys_freq, Tsys, ApEff_freq, ApEff = telescope_params(Tsys_file, ApEff_file)
    
    # Parkes Center Frequency
    center_freqs = [1280, 2432, 3520]
    nchans = [4608, 4608, 4096]
    chan_bw = 0.25 
    rfi_contamination = [0.1, 0.6, 0.85]
    
    diameter = 64.0  # Parkes diameter in meters
    Aphys = np.pi * (diameter / 2) ** 2 

    for i in range(len(center_freqs)):
        # interpolate Tsys and ApEff for nchans
        freq = np.linspace(center_freqs[i] - (nchans[i] * chan_bw / 2), 
                           center_freqs[i] + (nchans[i] * chan_bw / 2), 
                           nchans[i])
        T_sys = np.interp(freq, Tsys_freq, Tsys)
        eta = np.interp(freq, ApEff_freq, ApEff)
        
        T_sys_fctr = T_sys[find_nearest(Tsys_freq, center_freqs[i])]
        eta_fctr = eta[find_nearest(ApEff_freq, center_freqs[i])]
        
        np.random.seed(42)  

        rfi_mask = np.random.rand(len(freq)) <  rfi_contamination[i]
        
        
        print(f"\nCalculating Parkes Smin for center frequency: {center_freqs[i]} MHz")
        print(f"Tsys: {T_sys_fctr:.3f}")
        print(f"Aperture Efficiency: {eta_fctr:.3f}")
        print(f"Collecting Area: {Aphys*eta_fctr:.3f} m²")
        print(f"Bandwidth: {nchans[i] * chan_bw} MHz")
        print(f"Usable Channels: {rfi_contamination[i] * 100:.1f}%")
        print(f"RFI Mask: {np.sum(rfi_mask)} out of {len(freq)} channels are usable.")
        
        S_min_mJy = smin_quadrature(freq=freq,
                            T_sys=T_sys,
                            eta=eta,
                            A_phys=Aphys,
                            SNR_limit=SNR_limit,
                            T_obs=T_obs,
                            chan_BW=chan_bw,
                            dc=0.1,
                            n_p=2, 
                            rfi_mask=rfi_mask)
        print(f"Minimum Detectable Flux Density (S_min): {S_min_mJy:.3f} mJy")
        
        
    # GBT Calculation
    Tsys_file = "GBT_Tsys+Tsky.txt"
    ApEff_file = "GBT_AprEff.txt"
    Tsys_freq, Tsys, ApEff_freq, ApEff = telescope_params(Tsys_file, ApEff_file)
    
    
    center_freqs = [820, 1420, 2380]
    nchans = [2048, 2048, 2048]
    chan_bw = [0.117, 0.28, 0.42]
    
    diameter = 100  # Parkes diameter in meters
    Aphys = np.pi * (diameter / 2) ** 2 
    
    for i in range(len(center_freqs)):
        # interpolate Tsys and ApEff for nchans
        freq = np.linspace(center_freqs[i] - (nchans[i] * chan_bw[i] / 2), 
                           center_freqs[i] + (nchans[i] * chan_bw[i] / 2), 
                           nchans[i])
        T_sys = np.interp(freq, Tsys_freq, Tsys)
        eta = np.interp(freq, ApEff_freq, ApEff)
        
        T_sys_fctr = T_sys[find_nearest(Tsys_freq, center_freqs[i])]
        eta_fctr = eta[find_nearest(ApEff_freq, center_freqs[i])]
        
        np.random.seed(42)  

        rfi_mask = np.random.rand(len(freq)) < 0.95
        
        print(f"\nCalculating GBT Smin for center frequency: {center_freqs[i]} MHz")
        print(f"Tsys: {T_sys_fctr:.3f}")
        print(f"Aperture Efficiency: {eta_fctr:.3f}")
        print(f"Collecting Area: {Aphys*eta_fctr:.3f} m²")
        print(f"Bandwidth: {nchans[i] * chan_bw[i]} MHz")
        print(f"Usable Channels: {np.sum(rfi_mask)} out of {len(freq)} channels are usable.")
        
        S_min_mJy = smin_quadrature(freq=freq,
                            T_sys=T_sys,
                            eta=eta,
                            A_phys=Aphys,
                            SNR_limit=SNR_limit,
                            T_obs=T_obs,
                            chan_BW=chan_bw[i],
                            dc=0.1,
                            n_p=2, 
                            rfi_mask=rfi_mask)
        print(f"Minimum Detectable Flux Density (S_min): {S_min_mJy:.3f} mJy")
    
        
        
# %%
