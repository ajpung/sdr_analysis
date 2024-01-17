import abc

from orekit.pyhelpers import absolutedate_to_datetime
from org.orekit.propagation.analytical.tle import TLEPropagator, TLE
from pydantic import BaseModel, Field


class Duration(BaseModel, abc.ABC):
    """
    Abstract class for defining the duration for a scenario.  All
    child classes will implement a `duration_s` method that will
    inform the scenario how many seconds to simulate
    """

    @property
    @abc.abstractmethod
    def duration_s(self) -> int:
        pass


class TimeDuration(Duration):
    """
    Simple class to specify directly how many seconds to run a scenario
    """

    seconds: int = Field(..., description="Duration in seconds")

    @property
    def duration_s(self) -> int:
        return self.seconds


class TLEOrbitDuration(Duration):
    """
    Class for defining the duration of a scenario based on the number
    of orbits of a spacecraft with a specified TLE
    """

    line_1: str = Field(...)
    line_2: str = Field(...)
    n_orbits: float = Field(...)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tle = TLE(self.line_1, self.line_2)
        self._propagator = TLEPropagator.selectExtrapolator(self._tle)
        self._orbital_period = self._propagator.getInitialState().getKeplerianPeriod()
        self._start_date = absolutedate_to_datetime(self._tle.getDate())

    @property
    def duration_s(self) -> int:
        return int(self.n_orbits * self._orbital_period)

    @property
    def start_date(self):
        return self._start_date
