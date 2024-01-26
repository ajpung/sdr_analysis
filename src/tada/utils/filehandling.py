import os
import numpy as np


def write_data(
    sample_rate: float, center_freq: float, freq_correction: float, samples: np.ndarray
):
    filedir = ".\\sample_data\\"
    filename = "rfdata_240126"
    filestr = filedir + filename
    header_str = (
        "sr="
        + str(sample_rate)
        + "; cf="
        + str(center_freq)
        + "; fc="
        + str(freq_correction)
    )
    np.savetxt(filestr, samples.view(float).reshape(-1, 2), header="")
    assert os.path.isfile(filestr)


def read_csv(filename: str) -> list[complex]:
    a = np.genfromtxt(filename, dtype=str)
    b = [complex(s.replace("(", "").replace(")", "")) for s in a]
    return b
