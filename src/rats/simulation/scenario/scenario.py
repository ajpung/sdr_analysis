import collections
import datetime
import itertools
from typing import List, Tuple, Union, Dict, MutableMapping

import numpy as np
from pydantic import Field, BaseModel

from rats.measurements.atmospheric_loss import AtmosphericLoss
from rats.measurements.base import Measurement
from rats.simulation import Asset
from rats.simulation.antennas.base import AntennaAction
from rats.simulation.scenario import TimeDuration, TLEOrbitDuration
from rats.simulation.scenario.antenna_pair import AntennaPair, AntennaMeasurementHistory


class Scenario(BaseModel):
    """
    This class is used to simulate the RF environment over some period of time.
    It will take simulate the communications between antennas and take measurements
    at the provided measurement interval over the defined duration.  It collects
    results which can be accessed after the run.
    """

    assets: List[Asset] = Field(..., description="A list of assets")
    measurement_interval_s: int = Field(
        ..., description="The interval at which to take measurements"
    )
    duration: Union[TimeDuration, TLEOrbitDuration] = Field(
        ..., description="Duration of the simulation"
    )
    measurements: List[Measurement] = Field([])
    start_time: datetime.datetime = Field(datetime.datetime.now())

    _transmitters: List[Tuple[Asset, str]]
    _receivers: List[Tuple[Asset, str]]
    _antenna_pairs: List[AntennaPair]
    _end_time: datetime.datetime
    _timestamps: np.ndarray
    _n_steps: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        n_unique = {asset.name for asset in self.assets}
        if len(n_unique) < len(self.assets):
            raise ValueError("All assets must have a unique name")

        self._transmitters = [
            (asset, antenna.name)
            for asset in self.assets
            for antenna in asset.antennas
            if AntennaAction.TRANSMIT in antenna.actions
        ]
        self._receivers = [
            (asset, antenna.name)
            for asset in self.assets
            for antenna in asset.antennas
            if AntennaAction.RECEIVE in antenna.actions
        ]

        # TODO: pairs should not be on the same asset
        self._antenna_pairs = [
            AntennaPair(
                tx_asset=x[0][0],
                tx_antenna_id=x[0][1],
                rx_asset=x[1][0],
                rx_antenna_id=x[1][1],
                measurement_history=AntennaMeasurementHistory(
                    duration_s=self.duration.duration_s,
                    measurement_interval_s=self.measurement_interval_s,
                    measurements=[AtmosphericLoss()],
                ),
            )
            for x in itertools.product(self._transmitters, self._receivers)
            if x[0][0].name != x[1][0].name
        ]
        self._end_time = self.start_time + datetime.timedelta(
            seconds=self.duration.duration_s
        )
        self._timestamps = np.arange(
            self.start_time,
            self._end_time,
            datetime.timedelta(seconds=self.measurement_interval_s),
        ).astype(datetime.datetime)
        self._n_steps = int(self.duration.duration_s / self.measurement_interval_s)

    def run(self):
        for idx, current_dt in enumerate(self._timestamps):
            [pair.simulate_to(current_dt) for pair in self._antenna_pairs]

    def collect_results(self) -> Tuple[np.ndarray, List[str]]:
        results: MutableMapping[str, List[float]] = collections.defaultdict(list)
        results_names: MutableMapping[str, List[str]] = collections.defaultdict(list)
        for pair in self._antenna_pairs:
            location_idx = []
            location_names = []
            for i, name in enumerate(pair.location_names):
                if (
                    name not in results_names["locations"]
                    and name not in location_names
                ):
                    location_idx.append(i)
                    location_names.append(name)

            results["locations"].append(pair.location_history[:, location_idx])
            results_names["locations"].extend(location_names)
            results["measurements"].append(pair.measurement_history)
            results_names["measurements"].extend(pair.measurement_names)

        locations = np.hstack(results["locations"])
        measurements = np.hstack(results["measurements"])
        timestamps = self._timestamps.reshape(-1, 1)
        result = np.hstack([timestamps, locations, measurements])
        names = ["t"] + results_names["locations"] + results_names["measurements"]
        return result, names

    @property
    def antenna_pairs(self) -> List[AntennaPair]:
        return self._antenna_pairs
