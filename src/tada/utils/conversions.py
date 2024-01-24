import numpy as np

from scipy.signal import welch
from typing import overload, Union
from tada.physics.constants import SPEED_OF_LIGHT


@overload
def freq_to_wvln(freq: float) -> float:
    ...


@overload
def freq_to_wvln(freq: np.ndarray) -> np.ndarray:
    ...


def freq_to_wvln(freq: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Standard conversion from frequency to wavelength.

    Args:
        freq - Frequency [MHz]
    Returns:
        wvln - Wavelength [m]
    """
    wvln = SPEED_OF_LIGHT / (freq * 1e6)
    return wvln


@overload
def wvln_to_freq(wvln: float) -> float:
    ...


@overload
def wvln_to_freq(wvln: np.ndarray) -> np.ndarray:
    ...


def wvln_to_freq(wvln: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Standard conversion from wavelength to frequency.

    Args:
        wvln - Wavelength [m]
    Returns:
        freq - Frequency [MHz]
    """
    freq = (SPEED_OF_LIGHT / (wvln)) * 1e-6
    return freq


@overload
def db_to_decimal(db: float) -> float:
    ...


@overload
def db_to_decimal(db: np.ndarray) -> np.ndarray:
    ...


def db_to_decimal(db: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Standard conversion from decibels [dB] to decimal loss.

    Args:
        db - Absolute power loss [dB]
    Returns:
        dm - Decimal loss
    """
    dm = 10 ** (db / 10) - 1
    return dm


'''
def power_to_spectrum(pwr: np.ndarray) -> np.ndarray:
    """
    Standard conversion from power to frequency array

    Args:
        pwr - Extracted radio signal 
    Returns:
        freq_arr - Converted frequency arrat
    """
    #signal = []
    sdr.sample_rate = 2.8e6
    sdr.center_freq = 93.3e6

    samples = sdr.read_samples(4000)
    #signal.append(samples)
    corr = 1.5
    sample_freq, power = welch(samples, fs=sdr.sample_rate, window="hann", nperseg=2048, scaling="spectrum")
    sample_freq = fftshift(sample_freq)
    power = fftshift(power)/corr
    print(sum(power))

    plt.figure(figsize=(9.84, 3.94))
    plt.plot((sample_freq+sdr.center_freq)/1e6, np.log10(power),linewidth=1)
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Relative power (dB)")
    plt.show()    
    assert False
'''
