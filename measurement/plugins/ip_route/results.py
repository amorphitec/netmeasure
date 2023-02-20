import typing
from dataclasses import dataclass

from measurement.results import MeasurementResult
from measurement.units import TimeUnit, StorageUnit, RatioUnit, NetworkUnit


@dataclass(frozen=True)
class IPRouteMeasurementResult(MeasurementResult):
    """Encapsulates the result from an IPRoute measurement."""

    host: typing.Optional[str]
    hop_count: typing.Optional[int]
    ip: typing.Optional[str]
    route: typing.Optional[list]
