import abc
from typing import Union, ClassVar

import numpy as np
from pydantic import Field, field_validator

from rats.data import PolymorphicBaseModel
from rats.simulation.antennas import Antenna


class Measurement(PolymorphicBaseModel, abc.ABC, polymorphic=True):
    type: ClassVar[str]

    nan_value: float = Field(
        np.nan,
        description="Value to be used as missing value. 'nan' or float value. Defaults to np.nan",
    )

    @classmethod
    @field_validator("nan_value", mode="before")
    def validate_nan_value(cls, nan_value: Union[float, str]) -> float:
        if isinstance(nan_value, str):
            if nan_value == "nan":
                return np.nan
            else:
                raise ValueError("Nan value was string but was not nan")
        return nan_value

    @abc.abstractmethod
    def process(
        self,
        *,
        tx_location: np.ndarray,
        rx_location: np.ndarray,
        tx_antenna: Antenna,
        rx_antenna: Antenna,
        line_of_sight: np.ndarray,
    ):
        pass
