import os
import numpy as np
from rtlsdr import RtlSdr


def single_read(samp_rate, cent_freq, freq_corr, num_samp, gain_type="auto"):
    sdr = RtlSdr()
    # configure device
    sdr.sample_rate = samp_rate  # Hz
    sdr.center_freq = cent_freq  # Hz
    sdr.freq_correction = freq_corr  # PPM
    sdr.gain = gain_type
    samples = sdr.read_samples(num_samp)
    corr = 1.5
    return samples
