#%%
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import scienceplots
plt.style.use(['science'])
from matplotlib.colors import LinearSegmentedColormap


if __name__ == "__main__":
    fits_file = '/Users/oj/Desktop/Crab_61073.8138772467_cfbf00000_01_01.px'  
    fits_file = fits.open(fits_file)
    
    # print(fits_file.info())
    
    pulse_width = (fits_file['META'].data[1][4])
    snr = (fits_file['META'].data[0][4])

    data = fits_file[0].data 
    axes_data = fits_file['AXES'].data

    pcolor_data = fits_file['PCOLOR'].data[0]
    intensity = pcolor_data[2]
    n = intensity.size

    ny = 62
    if n % ny != 0:
        raise ValueError(f"Intensity length {n} not divisible by {ny}")

    nx = n // ny
    spec_yx = intensity.reshape(ny, nx)   
    spec_xy = intensity.reshape(nx, ny)     
    print(spec_yx.shape, spec_xy.shape)
    
    freq_data = fits_file[6].data[0][1]
    time_data = fits_file[2].data[0][0]

    print(freq_data.min(), '--', freq_data.max(), 'MHz')
    print(time_data.min(), '--', time_data.max(), 's')

    vmin, vmax = np.percentile(spec_yx, [30, 90])
    
    overall_max = np.max(spec_yx)
    print("Overall max intensity:", overall_max)   
    
    plt.figure(figsize=(4, 6), dpi=300)
    i = 0 
    for spectra in spec_yx:
        # y_data =  (spectra / overall_max) + freq_data[i]
        y_data =  spectra + freq_data[i]
        plt.plot(time_data, y_data, color='gray', lw=0.5, alpha=0.5)
        i += 1

    # plt.xlim(time_data.min(), time_data.max())
    xcenter = (time_data.min() + time_data.max()) / 2
    xhalf_range = (time_data.max() - time_data.min()) / 2 * 0.8
    plt.xlim(xcenter - xhalf_range, xcenter + xhalf_range)
    plt.ylim(freq_data.min(), freq_data.max() + 1 )
    
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [MHz]')
# %%
