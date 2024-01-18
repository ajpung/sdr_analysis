from typing import Union, Tuple

import numpy as np
from rats.simulation.location import CoordinateSystem

from rats.simulation.asset import Asset
from rats.utils.coordinates import lla_to_ecef


def unpack_coordinates(
    arr: np.ndarray,
) -> Union[Tuple[float, float, float], Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Examines the dimension length of a coordinate array and resizes array dimensions
    to match downstream expected formats.

    Args:
        arr (np.ndarray): Array containing coordinate array

    Returns:
        Three dimension values of the input array.
    """
    if len(arr.shape) == 1:
        return arr[0], arr[1], arr[2]
    elif arr.shape[0] == 1:
        return arr[0, 0], arr[0, 1], arr[0, 2]
    else:
        return arr[:, 0], arr[:, 1], arr[:, 2]


def analytic_los(
    a0: np.ndarray,
    a1: np.ndarray,
) -> np.ndarray:
    """
    Calculates existence of line-of-sight between two assets. Closed form
    solution taken from: https://tinyurl.com/2md9aazc.

    Args:
        a0 (np.ndarray): Array containing X,Y,Z components of object
        a1 (np.ndarray): Array containing X,Y,Z components of object

    Returns:
        rat: Boolean array of where line of sight does (1) or does not (0) exist.
    """

    x0, y0, z0 = unpack_coordinates(a0)
    x1, y1, z1 = unpack_coordinates(a1)
    x2, y2, z2 = 0, 0, 0

    num = (x2 - x0) * (x1 - x0) + (y2 - y0) * (y1 - y0) + (z2 - z0) * (z1 - z0)
    den = (x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0) + (z1 - z0) * (z1 - z0)
    rat = num / den
    return np.where(((rat > 0.99) | (rat < 0)), True, False)


def asset_line_of_sight(
    asset0: Asset,
    asset1: Asset,
) -> np.ndarray:
    """
    Parses RATS asset object information to feed into the analytic line of sight
    algorithm.

    Args:
        asset0 (object): RATS asset object with characterized antenna
        asset1 (object): RATS asset object with characterized antenna

    Returns:
        rat: Boolean array of where line of sight does (1) or does not (0) exist.
    """
    if asset0.location.coordinate_system == CoordinateSystem.LLA:
        a0_coordinates = lla_to_ecef(asset0.location.get_coordinates(), deg=True)
    else:
        a0_coordinates = asset0.location.get_coordinates()

    if asset1.location.coordinate_system == CoordinateSystem.LLA:
        a1_coordinates = lla_to_ecef(asset1.location.get_coordinates(), deg=True)
    else:
        a1_coordinates = asset1.location.get_coordinates()

    return analytic_los(a0_coordinates, a1_coordinates)
