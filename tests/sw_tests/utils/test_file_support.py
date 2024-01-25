import numpy as np
import pandas as pd

from tada.utils.filehandling import *

def test_file_read():
    filename = "./sample_data/sample_radio_data.csv"
    data = read_csv(filename)
    assert abs(np.real(data[13]) + 0.2627450980) < 1e-6
    assert abs(np.imag(data[57]) - 0.0117647058) < 1e-6
    assert abs(np.abs(data[100]) - 0.1294711687) < 1e-6