import datetime

import numpy as np
import pytest

from rats.physics.constants import EQ_RADIUS_M
from rats.simulation.antennas import DipoleAntenna, TurnstileAntenna
from rats.simulation.antennas.base import AntennaAction
from rats.simulation.asset import Asset
from rats.simulation.location import (
    CoordinateSystem,
)
from rats.simulation.location.dynamic import ArrayLocationProvider
from rats.simulation.location.dynamic.base import DynamicLocation, LocationProvider
from rats.simulation.location.fixed import LLALocation


@pytest.fixture(scope="module")
def spacecraft_location_provider() -> LocationProvider:
    a0_locations = np.array(
        [
            [33.1 for _ in range(-180, 181)],
            [float(x) for x in range(-180, 181)],
            [float(EQ_RADIUS_M + 500000) for _ in range(-180, 181)],
        ]
    ).T
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(seconds=5 * len(a0_locations))
    a0_timestamps = np.arange(
        datetime.datetime.now(), end_time, datetime.timedelta(seconds=5)
    )
    return ArrayLocationProvider(timestamps=a0_timestamps, locations=a0_locations)


@pytest.fixture(scope="module")
def simple_assets(spacecraft_location_provider):
    return [
        Asset(
            name="Spacecraft",
            location=DynamicLocation(
                coordinate_system=CoordinateSystem.LLA,
                location_provider=spacecraft_location_provider,
            ),
            antennas=[DipoleAntenna(), TurnstileAntenna()],
        ),
        Asset(
            name="ATL",
            location=LLALocation(coordinates=np.array([33.0, -84.0])),
            antennas=[DipoleAntenna(actions=[AntennaAction.TRANSMIT])],
        ),
        Asset(
            name="OTHER",
            location=LLALocation(coordinates=np.array([33.0, 84.0])),
            antennas=[DipoleAntenna(actions=[AntennaAction.TRANSMIT])],
        ),
    ]
