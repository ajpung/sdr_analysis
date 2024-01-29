import numpy as np
import pandas as pd

from scipy.signal import welch
from scipy.signal import find_peaks
from tada.utils.filehandling import *
from scipy.fftpack import fft, fftfreq, fftshift


def test_addition():
    a = 2
    b = 4
    assert a + b == 6


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
    peaks, _ = find_peaks(np.log10(power), threshold=0.005)
    assert np.max(freqs[peaks]) == 71.021
