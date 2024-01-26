import numpy as np
import matplotlib.pyplot as plt

from rtlsdr import RtlSdr
from scipy.signal import welch
from scipy.fftpack import fft, fftfreq, fftshift

# from scipy.signal import find_peaks
# import matplotlib.pyplot as plt


def test_data_read():
    sdr = RtlSdr()
    # configure device
    sdr.sample_rate = 3.2e6  # Hz
    sdr.center_freq = 93.3e6  # Hz
    sdr.freq_correction = 10  # PPM
    sdr.gain = "auto"
    samples = sdr.read_samples(200000)
    corr = 1.5
    assert len(samples) == 200000


def test_sample_types():
    sdr = RtlSdr()
    sdr.sample_rate = 2.8e6
    sdr.center_freq = 93.3e6
    samples = sdr.read_samples(4000)
    assert type(samples) == np.ndarray
    assert type(samples[0]) == np.complex128


"""
sdr.sample_rate = 3.2e6  # Hz
sdr.center_freq = 93.3e6  # Hz
sdr.freq_correction = 10  # PPM
sdr.gain = "auto"
samples = sdr.read_samples(200000)
corr = 1.5
sample_freq, power = welch(samples, fs=sdr.sample_rate, window="hann", nperseg=2048, scaling="spectrum")
sample_freq = fftshift(sample_freq)
power = fftshift(power)/corr
freqs = (sample_freq+sdr.center_freq)/1e6
print(sum(power))
plt.figure(figsize=(9.84, 3.94))
plt.plot(freqs, power,"-r",linewidth=0.5)
plt.xlabel("Frequency (MHz)")
plt.ylabel("Relative power (dB)")
plt.show()
plt.figure(figsize=(9.84, 3.94))
plt.plot(freqs, np.log10(power),"-r",linewidth=0.5, )
plt.xlabel("Frequency (MHz)")
plt.ylabel("Relative power (dB)")
plt.show()
header_str = "sr=" + str(sdr.sample_rate) + "; cf=" + str(sdr.center_freq) + "; fc=" + str(sdr.freq_correction)
np.savetxt('C:\\Users\\aaron\\Desktop\\outfile.txt', samples.view(float).reshape(-1, 2),header='')
#peaks, _ = find_peaks(np.log10(power), height=0)
#print(peaks)
#plt.plot(power)
#plt.plot(peaks, x[peaks], "x")
#plt.plot(np.zeros_like(x), "--", color="gray")
#plt.show()
"""
