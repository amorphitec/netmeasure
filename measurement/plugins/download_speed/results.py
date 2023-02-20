import typing
from dataclasses import dataclass

from measurement.results import MeasurementResult
from measurement.units import NetworkUnit, StorageUnit


@dataclass(frozen=True)
class DownloadSpeedMeasurementResult(MeasurementResult):
    """Encapsulates the results from a download speed measurement.

    :param url: The URL that was used to perform the download speed
    measurement.
    :param download_size: The size of the download (excluding units)
    that was used to perform the download speed measurement.
    :param download_size_unit: The unit of measurement used
    to describe the `download_size`.
    :param download_rate: The rate measured in the download speed
    measurement excluding units:
    :param download_rate_unit: The unit of measurement used to
    measure the `download_rate`.
    """

    url: str
    download_size: typing.Optional[float]
    download_size_unit: typing.Optional[StorageUnit]
    download_rate: typing.Optional[float]
    download_rate_unit: typing.Optional[NetworkUnit]
