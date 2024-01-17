import abc
import datetime
from typing import Literal, ClassVar, Any

import numpy as np
from pydantic import Field, ConfigDict, model_validator

from rats import Simulated
from rats.data import PolymorphicBaseModel
from rats.simulation.location import Location, CoordinateSystem


class LocationProvider(PolymorphicBaseModel, Simulated, abc.ABC, polymorphic=True):
    """
    This class represents a service to provide location coordinates for an asset.
    The asset is characterized by a `current_location`; if no location is provided,
    the service is able to generate one.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    @abc.abstractmethod
    def current_location(self) -> np.ndarray:
        pass

    @property
    @abc.abstractmethod
    def current_date(self) -> datetime.datetime:
        pass


class DynamicLocation(Location, abc.ABC):
    """
    This location can be expanded to connect to external systems and stream
    locations in via api or generator.  For now the only implementation
    of this class is a simple in memory provider.
    """

    type: ClassVar[Literal["DYNAMIC"]] = "DYNAMIC"
    coordinate_system_: CoordinateSystem = Field(
        ..., description="Coordinate system for the location", alias="coordinate_system"
    )
    location_provider: LocationProvider = Field(
        ...,
        description="A provider for location coordinates",
    )

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(
            coordinates=kwargs["location_provider"].current_location,
            **kwargs,
        )

    def get_coordinates(self) -> np.ndarray:
        return self.location_provider.current_location

    def simulate_to(self, dt: datetime.datetime):
        self.location_provider.simulate_to(dt)

    @staticmethod
    def validate_coordinates(coordinates: np.ndarray) -> np.ndarray:
        return coordinates

    @property
    def coordinate_system(self) -> CoordinateSystem:
        return self.coordinate_system_

    @property
    def current_location(self) -> np.ndarray:
        return self.location_provider.current_location
