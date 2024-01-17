import abc
import datetime
from typing import Literal, ClassVar

import numpy as np

from rats.physics.constants import EQ_RADIUS_M
from rats.simulation.location.base import CoordinateSystem, ArrayLike, Location


class FixedLocation(Location, abc.ABC, polymorphic=True):
    @property
    def current_location(self) -> np.ndarray:
        return self.coordinates


class ECILocation(FixedLocation):
    type: ClassVar[Literal["ECI_FIXED"]] = "ECI_FIXED"
    coordinate_system: ClassVar[Literal[CoordinateSystem.ECI]] = CoordinateSystem.ECI

    @staticmethod
    def validate_coordinates(coordinates: np.ndarray) -> np.ndarray:
        return coordinates

    def simulate_to(self, dt: datetime.datetime):
        pass


class LLALocation(FixedLocation):
    type: ClassVar[Literal["LLA_FIXED"]] = "LLA_FIXED"
    coordinate_system: ClassVar[Literal[CoordinateSystem.LLA]] = CoordinateSystem.LLA

    @staticmethod
    def validate_coordinates(coordinates: np.ndarray) -> np.ndarray:
        if len(coordinates.shape) == 1 and coordinates.shape[0] == 2:
            coordinates = np.append(coordinates, EQ_RADIUS_M)
        elif len(coordinates.shape) == 2 and coordinates.shape[1] == 2:
            altitude = np.full((coordinates.shape[0], 1), EQ_RADIUS_M)
            coordinates = np.hstack((coordinates, altitude))
        return coordinates

    def simulate_to(self, dt: datetime.datetime):
        pass
