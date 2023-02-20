import typing
from dataclasses import dataclass

from measurement.results import MeasurementResult
from measurement.units import TimeUnit, StorageUnit, RatioUnit, NetworkUnit


@dataclass(frozen=True)
class SpeedtestdotnetMeasurementResult(MeasurementResult):
    """Encapsulates the results from a speedtestdotnet measurement.

    :param download_rate: The measured download rate.
    :param download_rate_unit: The unit of measurement of `download_rate`.
    :param upload_rate: The measured upload rate.
    :param upload_rate_unit: The unit of measurement of `upload_rate`.
    :param data_received: The quantity of data report by the speedtest utility
    :param data_received_unit: The unit of measurement of `data_received`
    :param latency: The measured latency.
    :param server_name: The name of the speedtest.net server used to perform
    the speedtestdotnet measurement.
    :param server_id: The id of the speedtest.net server used to perform the
    speedtestdotnet measurement.
    :param server_sponsor: The sponsor of the speedtest.net server used to
    perform the speedtestdotnet measurement.
    :param server_host: The host name of the speedtest.net server used to
    perform the speedtestdotnet measurement.
    """

    download_rate: typing.Optional[float]
    download_rate_unit: typing.Optional[NetworkUnit]
    upload_rate: typing.Optional[float]
    upload_rate_unit: typing.Optional[NetworkUnit]
    data_received: typing.Optional[float]
    data_received_unit: typing.Optional[StorageUnit]
    latency: typing.Optional[float]
    server_name: typing.Optional[str]
    server_id: typing.Optional[str]
    server_sponsor: typing.Optional[str]
    server_host: typing.Optional[str]
