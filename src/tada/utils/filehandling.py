import numpy as np


def read_csv(filename: str) -> list[complex]:
    a = np.genfromtxt(filename, dtype=str)
    b = [complex(s.replace("(", "").replace(")", "")) for s in a]
    return b
