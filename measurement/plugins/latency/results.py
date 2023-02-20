import typing
from dataclasses import dataclass

from measurement.results import MeasurementResult
from measurement.units import TimeUnit, StorageUnit, RatioUnit


@dataclass(frozen=True)
class LatencyMeasurementResult(MeasurementResult):
    """Encapsulates the results from a latency measurement.

    :param host: The host that was used to perform the latency
    measurement.
    :param minimum_latency: The minimum amount of latency witnessed
    while performing the measurement.
    :param average_latency: The average amount of latency witnessed
    while performing the measurement.
    :param maximum_latency: The maximum amount of latency witnessed
    while performing the measurement.
    :param median_deviation: The median deviation witnessed across
    the measurement.
    """

    host: str
    minimum_latency: typing.Optional[float]
    average_latency: typing.Optional[float]
    maximum_latency: typing.Optional[float]
    median_deviation: typing.Optional[float]
    packets_transmitted: typing.Optional[int]
    packets_received: typing.Optional[int]
    packets_lost: typing.Optional[float]
    packets_lost_unit: typing.Optional[RatioUnit]
    elapsed_time: typing.Optional[float]
    elapsed_time_unit: typing.Optional[TimeUnit]


@dataclass(frozen=True)
class LatencyIndividualMeasurementResult(MeasurementResult):
    host: str
    packet_size: typing.Optional[float]
    packet_size_unit: typing.Optional[StorageUnit]
    reverse_dns_address: typing.Optional[str]
    ip_address: typing.Optional[str]
    icmp_sequence: typing.Optional[int]
    time_to_live: typing.Optional[float]
    elapsed_time: typing.Optional[float]
    elapsed_time_unit: typing.Optional[TimeUnit]
