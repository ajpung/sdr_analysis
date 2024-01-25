import numpy as np
import matplotlib.pyplot as plt

from rtlsdr import RtlSdr
from scipy.signal import welch
from scipy.fftpack import fft, fftfreq, fftshift


def test_data_read():
    sdr = RtlSdr()
    # configure device
    sdr.sample_rate = 2.048e6  # Hz
    sdr.center_freq = 70e6  # Hz
    sdr.freq_correction = 60  # PPM
    sdr.gain = "auto"
    samples = sdr.read_samples(512)
    assert len(samples) == 512


#def test_spectrum_convert():
#    sdr = RtlSdr()
#    sdr.sample_rate = 2.8e6
#    sdr.center_freq = 93.3e6
#    samples = sdr.read_samples(4000)
#    assert type(samples) == np.ndarray
#    assert type(samples[0]) == np.complex128


"""
def test_spectrum_convert():
    sdr = RtlSdr()
    #signal = []
    sdr.sample_rate = 2.8e6
    sdr.center_freq = 93.3e6

    samples = sdr.read_samples(4000)
    #signal.append(samples)
    corr = 1.5
    sample_freq, power = welch(samples, fs=sdr.sample_rate, window="hann", nperseg=2048, scaling="spectrum")
    sample_freq = fftshift(sample_freq)
    power = fftshift(power)/corr
    print(sum(power))

    plt.figure(figsize=(9.84, 3.94))
    plt.plot((sample_freq+sdr.center_freq)/1e6, np.log10(power),linewidth=1)
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Relative power (dB)")
    plt.show()    
    assert False
"""
