import datetime
import typing

import numpy as np
import numpy.typing as npt
from pydantic import Field, field_validator, model_validator

from rats.simulation.location.dynamic.base import LocationProvider


class ArrayLocationProvider(LocationProvider):
    """
    Provides locations from a provided array of locations. Timestamps should correspond exactly to
    timestamps at each measurement interval. The timestamps input array is separate but each entry should
    refer to the value in the locations data at the corresponding index. As such, the timestamps and locations
    arrays should have the same number of rows. Timestamps and locations should be sorted by time, with the
    earliest value appearing first (index 0)

    Args:
        timestamps (np.ndarray): Input array of timestamps for each location
        locations (np.ndarray): Input array of locations corresponding to each timestamp
    """

    type: typing.ClassVar[
        typing.Literal["ArrayLocationProvider"]
    ] = "ArrayLocationProvider"

    timestamps: np.ndarray = Field(
        ..., description="Input array of timestamps for each location"
    )
    locations: np.ndarray = Field(
        ..., description="Input array of locations corresponding to each timestamp"
    )

    _curr_idx = 0

    @field_validator("locations", mode="before")
    def validate_coordinates_input(cls, locations: npt.ArrayLike) -> np.ndarray:
        arr = np.asarray(locations)
        if len(arr.shape) == 1:
            assert arr.shape[0] == 3, "Location must have three elements"
            arr = arr.reshape(1, -1)
        else:
            assert arr.shape[1] == 3, "Location must have exactly three columns"
        return arr

    @model_validator(mode="after")
    def check_array_shapes(self) -> "ArrayLocationProvider":
        if self.timestamps.shape[0] != self.locations.shape[0]:
            raise ValueError(
                f"Timestamps and locations must have the same number of rows."
            )
        return self

    @property
    def current_location(self) -> np.ndarray:
        return typing.cast(np.ndarray, self.locations[self._curr_idx])

    @property
    def current_date(self) -> datetime.datetime:
        return typing.cast(datetime.datetime, self.timestamps[self._curr_idx])

    def simulate_to(self, dt: datetime.datetime):
        self._curr_idx += 1
