#%%
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import scienceplots
plt.style.use(['science'])
from matplotlib.colors import LinearSegmentedColormap


if __name__ == "__main__":
    fits_file = '/Users/oj/Desktop/J0520-25_59251.0042592558_cfbf00000_01_01.px'  
    fits_file = fits.open(fits_file)

    data = fits_file[0].data 
    axes_data = fits_file['AXES'].data

    pcolor_data = fits_file['PCOLOR'].data[0]
    intensity = pcolor_data[2] 
    spectrum = intensity.reshape((64, 270))

    freq_data = fits_file[6].data[0][1]
    time_data = fits_file[2].data[0][0]

    print(freq_data.min(), '--', freq_data.max(), 'MHz')
    print(time_data.min(), '--', time_data.max(), 's')

    vmin, vmax = np.percentile(spectrum, [30, 90])

    avg_spectrum = np.mean(spectrum, axis=0)

    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(4, 5), sharex=True, gridspec_kw={'height_ratios': [1, 4]}, dpi=150)
    fig.subplots_adjust(hspace=0)
    fig.subplots_adjust(hspace=0, top=0.95) 


    ax0.plot(time_data, avg_spectrum / np.max(avg_spectrum), color='black', lw=0.8)
    ax0.set_ylabel('Intensity [A.U.]', labelpad=8)
    ax0.tick_params(labelbottom=False)

    # Plot the dynamic spectrum below
    im = ax1.imshow(
        spectrum,
        aspect='auto',
        cmap='RdPu',
        extent=[time_data[0], time_data[-1], freq_data[0], freq_data[-1]],
        origin='upper'
    )

    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Frequency (MHz)')

    plt.show()