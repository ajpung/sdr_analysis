import math
import numpy as np

# from rats.physics.constants import EQ_RADIUS_M, EARTH_ECCEN, POLAR_RADIUS_M


'''
def lla_to_ecef(lla: np.ndarray, deg: bool = False) -> np.ndarray:
    """
    Uses the algorithm provided in "Understanding GPS Principles and Applications,
    Second Edition", page 31.

    Args:
        lla - Latitude [rad] / Longitude [rad] / Altitude [m]
        deg - Defaults to False, if True input assumed degrees and is converted
              to radians.
    Returns:
        ecef - X,Y,Z position in ecef frame [m]
    """
    if len(lla.shape) == 1:
        lla = lla.reshape((1, 3))
    if deg:
        latitude = np.deg2rad(lla[:, 0])
        longitude = np.deg2rad(lla[:, 1])
    else:
        latitude = lla[:, 0]
        longitude = lla[:, 1]
    altitude = lla[:, 2]

    ecef = np.zeros_like(lla)

    ecef[:, 0] = (EQ_RADIUS_M * np.cos(longitude)) / np.sqrt(
        1.0 + (1.0 - EARTH_ECCEN) * (np.tan(latitude)) ** 2
    ) + altitude * np.cos(longitude) * np.cos(latitude)

    ecef[:, 1] = (EQ_RADIUS_M * np.sin(longitude)) / np.sqrt(
        1.0 + (1.0 - EARTH_ECCEN) * (np.tan(latitude)) ** 2
    ) + altitude * np.sin(longitude) * np.cos(latitude)

    ecef[:, 2] = (EQ_RADIUS_M * (1.0 - EARTH_ECCEN) * np.sin(latitude)) / np.sqrt(
        1.0 - EARTH_ECCEN * (np.sin(latitude)) ** 2
    ) + altitude * np.sin(latitude)

    if ecef.shape[0] == 1:
        return ecef.flatten()
    return ecef
'''
