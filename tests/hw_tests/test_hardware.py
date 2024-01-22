from rtlsdr import RtlSdr


def test_data_read():
    sdr = RtlSdr()
    # configure device
    sdr.sample_rate = 2.048e6  # Hz
    sdr.center_freq = 70e6  # Hz
    sdr.freq_correction = 60  # PPM
    sdr.gain = "auto"
    samples = sdr.read_samples(512)
    assert len(samples) == 512
