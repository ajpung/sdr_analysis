import datetime
from enum import Enum
from typing import List, Annotated, Union, TypeVar

import numpy as np
from pydantic import BaseModel, Field

from rats.simulation.antennas import (
    Antenna,
    DipoleAntenna,
    TurnstileAntenna,
    YagiUda2DAntenna,
    YagiUda3DAntenna,
)
from rats.simulation.location import CoordinateSystem, Location
from rats.utils.coordinates import ecef_to_lla, lla_to_ecef


class AssetAction(str, Enum):
    TRANSMIT = "TRANSMIT"
    RECEIVE = "RECEIVE"


AntennaType = Annotated[  # type: ignore
    Union[
        DipoleAntenna,
        TurnstileAntenna,
        YagiUda2DAntenna,
        YagiUda3DAntenna,
    ],
    Field(discriminator="geometry_type"),
]

#
# Annotated[  # type: ignore
#     Union[Location.get_subclasses()], Field(discriminator="location_type")
# ]

LocationType = TypeVar("LocationType", bound=Location)


class Asset(BaseModel):
    """This class represents a RATS asset object. Conceptually, each asset
    represents a space-, air-, land-, or water-based vehicle or station capable
    of receiving or transmitting RF signals.

    In turn, each asset is characterized by a descriptive name field (`name`), a
    location field (`location`), and a list of attributed antenna objects
    (`antennas`). Antennas can be added to each asset via the `add_antenna`
    method.
    """

    name: str = Field(..., description="Name of the asset")
    location: Location = Field(..., description="Location of the asset")
    antennas: List[Antenna] = Field(
        [], description="Antennas associated with the asset"
    )
    _current_dt = None

    def add_antenna(self, antenna: Antenna):
        self.antennas.append(antenna)

    def current_location(self, coordinate_system: CoordinateSystem) -> np.ndarray:
        if coordinate_system == self.location.coordinate_system:
            return self.location.current_location
        elif (
            self.location.coordinate_system == CoordinateSystem.ECI
            and coordinate_system == CoordinateSystem.LLA
        ):
            return ecef_to_lla(self.location.current_location, deg=True)
        elif (
            self.location.coordinate_system == CoordinateSystem.LLA
            and coordinate_system == CoordinateSystem.ECI
        ):
            return lla_to_ecef(self.location.current_location, deg=True)
        else:
            raise ValueError(f"Unrecognized coordinate system: {coordinate_system}")

    def get_antenna_location(
        self, name: str, coordinate_system: CoordinateSystem
    ) -> np.ndarray:
        """
        This doesnt really make sense right now because the units don't match up
        TODO: Make this make sense

        Args:
            name (str): Name of Antenna
            coordinate_system (CoordinateSystem): The desired coordinate system of the location

        Returns:
            (np.ndarray): The current location of the antenna in the desired coordinate system
        """
        antenna_location: np.ndarray = (
            self.current_location(coordinate_system)
            + self.get_antenna(name).relative_location
        )
        return antenna_location

    def get_antenna(self, name: str) -> Antenna:
        for antenna in self.antennas:
            if antenna.name == name:
                return antenna
        else:
            raise ValueError(f"No antenna with name: {name}")

    def simulate_to(self, dt: datetime.datetime):
        if self._current_dt is None or dt > self._current_dt:
            self.location.simulate_to(dt)
            [antenna.simulate_to(dt) for antenna in self.antennas]
            self._current_dt = dt
