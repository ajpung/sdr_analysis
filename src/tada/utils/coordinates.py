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


def ecef_to_lla(ecef: np.ndarray, deg: bool = False) -> np.ndarray:
    """
    Uses the algorithm provided in "Understanding GPS Principles and Applications,
    Second Edition" to convert ECEF to LLA with WGS-84 ellipsoid.

    Args:
        ecef - X / Y / Z
        deg - Defaults to False, if True output is returned in degrees.

    Returns:
        lla - Latitude, Longitude, Altitude position in LLA frame
    """
    if len(ecef.shape) == 1:
        ecef = ecef.reshape((1, 3))

    x = ecef[:, 0]
    y = ecef[:, 1]
    z = ecef[:, 2]

    # --- derived constants
    e = (
        math.sqrt(math.pow(EQ_RADIUS_M, 2.0) - math.pow(POLAR_RADIUS_M, 2.0))
        / EQ_RADIUS_M
    )
    clambda = np.arctan2(y, x)
    p = np.sqrt(pow(x, 2.0) + pow(y, 2))
    h_old = 0.0

    theta = np.arctan2(z, p * (1.0 - math.pow(e, 2.0)))
    cs = np.cos(theta)
    sn = np.sin(theta)
    N = np.power(EQ_RADIUS_M, 2.0) / np.sqrt(
        np.power(EQ_RADIUS_M * cs, 2.0) + np.power(POLAR_RADIUS_M * sn, 2.0)
    )
    h = p / cs - N

    # Iteratively estimate altitude
    while np.any(abs(h - h_old) > 2e-5):
        h_old = h
        theta = np.arctan2(z, p * (1.0 - np.power(e, 2.0) * N / (N + h)))
        cs = np.cos(theta)
        sn = np.sin(theta)
        N = np.power(EQ_RADIUS_M, 2.0) / np.sqrt(
            np.power(EQ_RADIUS_M * cs, 2.0) + np.power(POLAR_RADIUS_M * sn, 2.0)
        )
        h = p / cs - N

    if deg:
        lla = np.array([np.degrees(theta), np.degrees(clambda), h])
    else:
        lla = np.array([theta, clambda, h])
    return lla
'''
