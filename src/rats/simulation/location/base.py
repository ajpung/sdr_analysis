from __future__ import annotations

import abc
from enum import Enum
from typing import List, Union, Any, ClassVar

import numpy as np
from pydantic import Field, field_serializer, ConfigDict, field_validator

from rats import Simulated
from rats.data import PolymorphicBaseModel


class CoordinateSystem(str, Enum):
    """This class represents a coordinate system object. Conceptually, each asset
    and antenna in the simulator is defined within a specific GCS (geographic
    coordinate system) or ECI (Earth-centered inertial) reference frame.

    The GCS reference frame describes objects using latitude, longitude, and
    altitude; conversely, ECI describes objects using X, Y, and Z coordinates.
    Coordinates can be described in list or array formats.
    """

    LLA = "LLA"
    ECI = "ECI"


COORDINATE_SYSTEM_NAMES = {
    CoordinateSystem.LLA: ["latitude", "longitude", "altitude"],
    CoordinateSystem.ECI: ["x", "y", "z"],
}

ArrayLike = Union[np.ndarray, List]


class Location(PolymorphicBaseModel, Simulated, abc.ABC, polymorphic=True):
    """This class represents an object's location defined by an array (or list)
    of coordinates and a defined location type (reference frame).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    coordinates: np.ndarray = Field(..., description="location coordinates")
    type: ClassVar[str]

    @field_validator("coordinates", mode="before")
    def validate_coordinates_input(cls, coordinates: Any) -> ArrayLike:
        return cls.process_coordinates(coordinates)

    @classmethod
    def process_coordinates(cls, coordinates: ArrayLike) -> np.ndarray:
        if isinstance(coordinates, list):
            coordinates = np.array(coordinates)
        if coordinates.dtype != np.float64:
            coordinates = coordinates.astype(np.float64)

        return cls.validate_coordinates(coordinates)

    def set_coordinates(self, coordinates: ArrayLike):
        self.coordinates = self.process_coordinates(coordinates)

    def get_coordinates(self) -> np.ndarray:
        return self.coordinates

    @property
    @abc.abstractmethod
    def current_location(self) -> np.ndarray:
        pass

    @property
    def names(self) -> List[str]:
        return COORDINATE_SYSTEM_NAMES[self.coordinate_system]

    @staticmethod
    @abc.abstractmethod
    def validate_coordinates(coordinates: np.ndarray) -> np.ndarray:
        pass

    @property
    @abc.abstractmethod
    def coordinate_system(self) -> CoordinateSystem:
        pass

    @field_serializer("coordinates")
    def serialize_coordinates(self, arr: np.ndarray, _info):
        return arr.tolist()
