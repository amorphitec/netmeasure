import typing
from dataclasses import dataclass

from netmeasure.measurements.base.results import MeasurementResult
from netmeasure.units import TimeUnit, StorageUnit, RatioUnit, NetworkUnit


@dataclass(frozen=True)
class YoutubeDownloadMeasurementResult(MeasurementResult):
    """Encapsulates the results from a YouTube measurement."""

    download_rate: typing.Optional[float]
    download_rate_unit: typing.Optional[NetworkUnit]
    download_size: typing.Optional[float]
    download_size_unit: typing.Optional[StorageUnit]
    url: typing.Optional[str]
    elapsed_time: typing.Optional[float]
    elapsed_time_unit: typing.Optional[TimeUnit]
