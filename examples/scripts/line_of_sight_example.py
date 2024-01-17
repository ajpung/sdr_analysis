import numpy as np
import pandas as pd

from rats.physics.constants import EQ_RADIUS_M
from rats.simulation.antennas.base import Antenna, AntennaGeometry
from rats.simulation.asset import Asset
from rats.simulation.locations import (
    GCSLocation,
    ArrayLocationProvider,
    MovingLocation,
    CoordinateSystem,
)
from rats.simulation.simulation import RATS

a0_locations = np.array(
    [
        [33.1 for _ in range(-180, 180)],
        [float(x) for x in range(-180, 180)],
        [float(EQ_RADIUS_M + 500000) for _ in range(-180, 180)],
    ]
).T

# this is a spacecraft because the altitude puts it in orbit
spacecraft_location_provider = ArrayLocationProvider(a0_locations)
spacecraft_location = MovingLocation(CoordinateSystem.LLA, spacecraft_location_provider)

# this carrier is docked near ATL (must be a big navy port there)
carrier = Asset(
    name="carrier",
    location=GCSLocation(np.array([33.0, -84.0])),
    antennas=[
        Antenna(
            geometry=AntennaGeometry.DIPOLE,
            frequency=400.0,
        )
    ],
)
simulation = RATS(assets=[carrier])

spacecraft = Asset(
    name="spacecraft", location=spacecraft_location, antennas=[Antenna()]
)
spacecraft.add_antenna(Antenna(geometry=AntennaGeometry.DIPOLE, frequency=400.0))

simulation.add_asset(spacecraft)

results, names = simulation.line_of_sight()

df = pd.DataFrame(results, columns=names)
