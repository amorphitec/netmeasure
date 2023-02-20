import typing
from dataclasses import dataclass

from measurement.results import MeasurementResult
from measurement.units import TimeUnit, StorageUnit, RatioUnit, NetworkUnit


@dataclass(frozen=True)
class WebpageMeasurementResult(MeasurementResult):
    """Encapsulates the results from a Webpage download measurement."""

    url: typing.Optional[str]
    download_rate: typing.Optional[float]
    download_rate_unit: typing.Optional[NetworkUnit]
    download_size: typing.Optional[float]
    download_size_unit: typing.Optional[StorageUnit]
    asset_count: typing.Optional[int]
    failed_asset_downloads: typing.Optional[int]
    elapsed_time: typing.Optional[float]
    elapsed_time_unit: typing.Optional[TimeUnit]
