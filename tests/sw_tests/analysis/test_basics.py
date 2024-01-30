import numpy as np

from scipy.signal import welch
from scipy.fftpack import fftshift
from scipy.signal import find_peaks
from tada.utils.filehandling import *


def test_find_peaks():
    sample_rate = 2.048e6  # Hz
    center_freq = 70e6  # Hz
    freq_correction = 60  # PPM
    gain = "auto"
    filename = "./sample_data/sample_radio_data.csv"
    samples = read_csv(filename)
    corr = 1.5
    sample_freq, power = welch(
        samples, fs=sample_rate, window="hann", nperseg=2048, scaling="spectrum"
    )
    sample_freq = fftshift(sample_freq)
    power = fftshift(power) / corr
    freqs = (sample_freq + center_freq) / 1e6
    avg_noise = np.average(power)
    peaks, _ = find_peaks(power, height=20 * avg_noise, distance=50)
    assert np.max(freqs[peaks]) == 70.576
    assert (peaks == np.array([267, 1074, 1600])).all()
    assert np.allclose(power[peaks], [0.00513358, 0.0047351, 0.00246171])
