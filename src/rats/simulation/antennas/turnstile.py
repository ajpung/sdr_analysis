import datetime
from typing import Literal, ClassVar

import math
import numpy as np
from pydantic import Field

from rats.simulation.antennas import Antenna


class TurnstileAntenna(Antenna):
    """
       Antennas are oriented such that the radiation generated by an ideal,
    symmetric, center-fed antenna propagates in the +Y direction. Using
    this logic, turnstile antennas are built in the X-Z plane.
    """

    type: ClassVar[Literal["TURNSTILE"]] = "TURNSTILE"
    n: float = Field(1, description="Total length of each dipole wrt wavelength")
    source_input_location: str = Field(
        "center", description="Location on the dipole where source is applied."
    )
    segments_per_arm: int = Field(
        5, description="Number of segments used to define the dipole wire."
    )

    def _initialize(self):
        arm_length = self.n / 2 * self._wvl
        # width = 0.02
        top = np.array([0.0, 0.0, arm_length])
        center = np.array([0.0, 0.0, 0.0])
        self.create_wire(
            tag_id=0, segments=self.segments_per_arm, wire_start=top, wire_end=center
        )

        left = np.array([-arm_length, 0.0, 0.0])
        self.create_wire(
            tag_id=1, segments=self.segments_per_arm, wire_start=left, wire_end=center
        )

        bottom = np.array([0.0, 0.0, -arm_length])
        self.create_wire(
            tag_id=2, segments=self.segments_per_arm, wire_start=bottom, wire_end=center
        )

        right = np.array([arm_length, 0.0, 0.0])
        self.create_wire(
            tag_id=3, segments=self.segments_per_arm, wire_start=right, wire_end=center
        )

    @property
    def diameter(self):
        return self.n * self._wvl

    def simulate_to(self, dt: datetime.datetime):
        return

    @property
    def source_index(self):
        if self.source_input_location == "center":
            return math.ceil(self.segments_per_arm)
        elif self.source_input_location == "start":
            return 1