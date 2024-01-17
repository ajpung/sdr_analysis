import datetime
import typing

import numpy as np
from pydantic import Field

from orekit.pyhelpers import datetime_to_absolutedate, absolutedate_to_datetime
from org.orekit.bodies import OneAxisEllipsoid
from org.orekit.frames import FramesFactory, ITRFVersion, StaticTransform
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from org.orekit.utils import AbsolutePVCoordinates, IERSConventions, Constants

from rats.physics.constants import EQ_RADIUS_M
from rats.simulation.location import CoordinateSystem
from rats.simulation.location.dynamic import LocationProvider


ITRF_FRAME = FramesFactory.getITRF(
    ITRFVersion.ITRF_2014, IERSConventions.IERS_2010, False
)

ONE_AXIS_ELLIPSOID_WGS84 = OneAxisEllipsoid(
    Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
    Constants.WGS84_EARTH_FLATTENING,
    ITRF_FRAME,
)

J2000 = FramesFactory.getEME2000()


def pv_to_lla(apv: AbsolutePVCoordinates) -> list:
    """
    Takes absolute PV coordinates and returns lat, lon, and alt
    """
    # Construct the transformation matrix from EMEJ2000 to ITRF coordinates (i.e. Earth-centered Earth-fixed)
    transform_frame = apv.getFrame().getTransformTo(ITRF_FRAME, apv.getDate())  # type: ignore
    static_transform = StaticTransform.cast_(transform_frame)  # type: ignore

    # Transform the position vector to ITRF frame
    itrf_position = static_transform.transformPosition(apv.position)

    # Transform the cartesian ITRF state to a surface relative point with respect to the WGS84 ellipsoid
    gp = ONE_AXIS_ELLIPSOID_WGS84.transform(itrf_position, ITRF_FRAME, apv.getDate())

    return [gp.latitude, gp.longitude, gp.altitude]


class TLELocationProvider(LocationProvider):
    """
    Location provider that uses Orekit to propagate TLEs for spacecraft locations.
    """

    line1: str = Field(..., description="TLE Line 1")
    line2: str = Field(..., description="TLE Line 2")
    coordinate_system: CoordinateSystem = Field(
        CoordinateSystem.LLA,
        description="Desired coordinate system for output coordinates",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tle = TLE(self.line1, self.line2)
        self._propagator = TLEPropagator.selectExtrapolator(self._tle)
        self._current_date = self._propagator.getInitialState().getDate()
        self._current_state = self._propagator.getInitialState()
        self._orbital_period = self._propagator.getInitialState().getKeplerianPeriod()

    @property
    def current_location(self) -> np.ndarray:
        if self.coordinate_system == CoordinateSystem.LLA:
            lat, lon, alt = pv_to_lla(
                AbsolutePVCoordinates(J2000, self._current_state.getPVCoordinates())
            )
            return np.array([np.rad2deg(lat), np.rad2deg(lon), alt + EQ_RADIUS_M])
        elif self.coordinate_system == CoordinateSystem.ECI:
            position = self._current_state.getPVCoordinates().getPosition()
            return np.array([position.getX(), position.getY(), position.getZ()])
        else:
            raise ValueError(f"Unknown coordinate system: {self._coordinate_system}")

    @property
    def current_date(self) -> datetime.datetime:
        return typing.cast(
            datetime.datetime, absolutedate_to_datetime(self._current_date)
        )

    def simulate_to(self, dt: datetime.datetime):
        self._current_date = datetime_to_absolutedate(dt)
        self._current_state = self._propagator.propagate(self._current_date)
