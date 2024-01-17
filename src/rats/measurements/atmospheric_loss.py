from typing import Optional, Literal, ClassVar

import itur
import numpy as np
from pydantic import Field

from rats.measurements.base import Measurement
from rats.simulation.antennas import Antenna


class AtmosphericLoss(Measurement):
    type: ClassVar[Literal["AtmosphericLoss"]] = "AtmosphericLoss"

    p: float = Field(1)
    hs: float = Field(0.031382984)
    eta: float = Field(0.65)
    tau: float = Field(0.0)

    def process(
        self,
        tx_location: np.ndarray,
        rx_location: np.ndarray,
        tx_antenna: Antenna,
        rx_antenna: Antenna,
        line_of_sight: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        Calculates signal attenuation due to atmospheric elements like gas, rain,
        clouds, or scintillation.

        @aaron: I believe all the other variables could
        be computed from the locations provided or from the provided antennas if we needed
        to populate the other args in the itur function.

        Args:
            tx_location (Asset): Transmitter Location in LLA
            rx_location (Asset): Receiver Location in LLA
            tx_antenna (Antenna): Transmitter Antenna
            rx_antenna (Antenna): Receiver Antenna
            line_of_sight (bool): Whether there is line of sight between the two antennas

        Returns:
            float: Total atmospheric loss [dB]
        """
        if tx_location.shape != rx_location.shape:
            raise ValueError(
                "Transmitter location shape and receiver location shape must match"
            )

        if len(tx_location.shape) == 1:
            tx_location = tx_location.reshape(1, -1)

        if len(rx_location.shape) == 1:
            rx_location = rx_location.reshape(1, -1)

        if line_of_sight is None:
            line_of_sight = np.ones((rx_location.shape[0], 1))

        if len(line_of_sight.shape) <= 1:
            line_of_sight = line_of_sight.reshape(1, -1)

        mask = np.where(line_of_sight)
        tx_location_los = tx_location[mask[0], :]
        rx_location_los = rx_location[mask[0], :]

        tx_lat, tx_lon, tx_alt = (
            tx_location_los[:, 0],
            tx_location_los[:, 1],
            tx_location_los[:, 2],
        )
        rx_lat, rx_lon, rx_alt = (
            rx_location_los[:, 0],
            rx_location_los[:, 1],
            rx_location_los[:, 2],
        )

        # Compute the elevation angle between satellite and ground station
        # we are assuming the satellite is the receiver
        # TODO: how do we compute elevation angle if we have two space objects?
        el = itur.utils.elevation_angle(
            rx_alt / 1000.0,
            rx_lat,
            rx_lon,
            tx_lat,
            tx_lon,
        )

        result = np.full_like(
            line_of_sight, fill_value=self.nan_value, dtype=np.float64
        )
        if line_of_sight.any():
            loss_db = itur.atmospheric_attenuation_slant_path(
                lat=tx_lat,
                lon=tx_lon,
                f=tx_antenna.frequency / 1000.0,
                el=el,
                D=rx_antenna.diameter,
                p=self.p,
                hs=self.hs,
                eta=self.eta,
                tau=self.tau,
            )
            result[mask] = loss_db.value

        return result
