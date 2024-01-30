import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import welch
from scipy.fftpack import fft, fftfreq, fftshift
from tada.utils.acquisition import single_read


def test_data_read():
    samp_rate = 3.2e6  # Hz
    cent_freq = 93.3e6  # Hz
    freq_corr = 10  # PPM
    num_samp = 200000
    samples = single_read(samp_rate, cent_freq, freq_corr, num_samp)
    assert len(samples) == 200000


def test_sample_types():
    samp_rate = 3.2e6  # Hz
    cent_freq = 103.7e6  # Hz
    freq_corr = 15  # PPM
    num_samp = 4000
    samples = single_read(samp_rate, cent_freq, freq_corr, num_samp)
    assert type(samples) == np.ndarray
    assert type(samples[0]) == np.complex128
