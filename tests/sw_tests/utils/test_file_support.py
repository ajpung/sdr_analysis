import numpy as np

from tada.utils.filehandling import *


def test_file_write():
    samples = np.random.uniform(-1, 1, 2000) + 1.0j * np.random.uniform(-1, 1, 2000)
    sample_rate = 3.2e6
    center_freq = 93.3e6
    freq_correction = 10
    write_data(sample_rate, center_freq, freq_correction, samples)
    filedir = ".\\sample_data\\"
    filename = "rfdata_240126"
    filestr = filedir + filename
    assert os.path.isfile(filestr)
    os.remove(filestr)


def test_file_read():
    filename = "./sample_data/sample_radio_data.csv"
    data = read_csv(filename)
    assert abs(np.real(data[13]) + 0.2627450980) < 1e-6
    assert abs(np.imag(data[57]) - 0.0117647058) < 1e-6
    assert abs(np.abs(data[100]) - 0.1294711687) < 1e-6
