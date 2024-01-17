import datetime
import math
from typing import List

import numpy as np

from rats import Simulated
from rats.analysis import analytic_los
from rats.measurements.base import Measurement
from rats.simulation import Asset
from rats.simulation.antennas.base import AntennaAction, Antenna
from rats.simulation.location import CoordinateSystem


class AntennaMeasurementHistory:
    """
    This class stores the history of measurements taken for a given
    antenna
    """

    def __init__(
        self,
        duration_s: float,
        measurement_interval_s: float,
        measurements: List[Measurement] | None = None,
    ):
        self._duration_s = duration_s
        self._measurement_interval_s = measurement_interval_s
        self._measurements = measurements or []
        self._measurements_idx = {
            measurement.type: i for i, measurement in enumerate(self._measurements)
        }
        n_steps = math.ceil(duration_s / measurement_interval_s)
        self._data = np.zeros((n_steps, len(self._measurements)))
        self._locations = np.zeros((n_steps, 6))
        self._timestamps = np.zeros(n_steps)
        self._curr_step = 0

    @property
    def measurement_types(self):
        return self._measurements

    @property
    def locations(self):
        return self._locations

    @property
    def measurements(self):
        return self._data

    def add_measurements(
        self,
        dt: datetime.datetime,
        tx_location: np.ndarray,
        rx_location: np.ndarray,
        values: np.ndarray,
    ):
        if values.shape[0] != len(self._measurements):
            raise ValueError("Must provide values for all measurements")

        self._timestamps[self._curr_step] = dt.timestamp()
        self._locations[self._curr_step, 0:3] = tx_location
        self._locations[self._curr_step, 3:6] = rx_location
        self._data[self._curr_step] = values
        self._curr_step += 1


class AntennaPair(Simulated):
    def __init__(
        self,
        *,
        tx_asset: Asset,
        tx_antenna_id: str,
        rx_asset: Asset,
        rx_antenna_id: str,
        measurement_history: AntennaMeasurementHistory,
    ):
        if AntennaAction.TRANSMIT not in tx_asset.get_antenna(tx_antenna_id).actions:
            raise ValueError(
                "Transmitting antenna must be able to transmit, check the assets allowable actions"
            )
        if AntennaAction.RECEIVE not in rx_asset.get_antenna(rx_antenna_id).actions:
            raise ValueError(
                "Receiving antenna must be able to receive, check the assets allowable actions"
            )

        self._tx_asset = tx_asset
        self._tx_antenna_id = tx_antenna_id
        self._rx_asset = rx_asset
        self._rx_antenna_id = rx_antenna_id
        self._history = measurement_history

    @property
    def transmitter_asset(self) -> Asset:
        return self._tx_asset

    @property
    def receiver_asset(self) -> Asset:
        return self._rx_asset

    @property
    def transmitter_antenna(self) -> Antenna:
        return self._tx_asset.get_antenna(self._tx_antenna_id)

    @property
    def receiver_antenna(self) -> Antenna:
        return self._rx_asset.get_antenna(self._rx_antenna_id)

    @property
    def location_history(self):
        return self._history.locations

    @property
    def location_names(self):
        return [
            "_".join([self._tx_asset.name, self._tx_antenna_id, "location_lat"]),
            "_".join([self._tx_asset.name, self._tx_antenna_id, "location_lon"]),
            "_".join([self._tx_asset.name, self._tx_antenna_id, "location_alt"]),
            "_".join([self._rx_asset.name, self._rx_antenna_id, "location_lat"]),
            "_".join([self._rx_asset.name, self._rx_antenna_id, "location_lon"]),
            "_".join([self._rx_asset.name, self._rx_antenna_id, "location_alt"]),
        ]

    @property
    def measurement_history(self):
        return self._history.measurements

    @property
    def measurement_names(self):
        return [
            "_".join(
                [
                    self._rx_asset.name,
                    self._rx_antenna_id,
                    self._tx_asset.name,
                    self._tx_antenna_id,
                    measurement.type,
                ]
            )
            for measurement in self._history.measurement_types
        ]

    def simulate_to(self, dt: datetime.datetime):
        self._tx_asset.simulate_to(dt)
        self._rx_asset.simulate_to(dt)
        tx_location_eci = self._tx_asset.get_antenna_location(
            self._tx_antenna_id, CoordinateSystem.ECI
        )
        rx_location_eci = self._rx_asset.get_antenna_location(
            self._rx_antenna_id, CoordinateSystem.ECI
        )
        tx_location_lla = self._tx_asset.get_antenna_location(
            self._tx_antenna_id, CoordinateSystem.LLA
        )
        rx_location_lla = self._rx_asset.get_antenna_location(
            self._rx_antenna_id, CoordinateSystem.LLA
        )
        los = analytic_los(tx_location_eci, rx_location_eci)
        values = []
        for i, measurement in enumerate(self._history.measurement_types):
            values.append(
                measurement.process(
                    tx_location=tx_location_lla,
                    rx_location=rx_location_lla,
                    tx_antenna=self._tx_asset.get_antenna(self._tx_antenna_id),
                    rx_antenna=self._rx_asset.get_antenna(self._rx_antenna_id),
                    line_of_sight=los,
                )
            )
        self._history.add_measurements(
            dt, tx_location_lla, rx_location_lla, np.array(values)
        )

    @property
    def identifier(self):
        return "_".join(
            [
                self._tx_asset.name,
                self._tx_antenna_id,
                self._rx_asset.name,
                self._rx_antenna_id,
            ]
        )
