import re
import subprocess

import validators
from validators import ValidationFailure

from netmeasure.measurements.base.measurements import BaseMeasurement
from netmeasure.measurements.latency.results import (
    LatencyMeasurementResult,
    LatencyIndividualMeasurementResult,
)
from netmeasure.measurements.base.results import Error
from netmeasure.units import RatioUnit, TimeUnit, StorageUnit

LATENCY_OUTPUT_REGEX = re.compile(
    r"= (?P<minimum_latency>[\d.].*)/(?P<average_latency>[\d.].*)/(?P<maximum_latency>[\d.].*)/(?P<median_deviation>[\d.].*) "
)
LATENCY_PACKETS_REGEX = re.compile(
    r"(?P<packets_transmitted>\d*) packets transmitted, (?P<packets_received>\d*) received, "
    r"(?P<packet_loss>\d*)% packet loss, time (?P<time>\d*)(?P<time_unit>.*)"
)
LATENCY_INDIVIDUAL_PING_REGEX = re.compile(
    r"(?P<packet_size>\d*) (?P<packet_size_units>.*) from (?P<reverse_dns_address>.*) \(("
    r"?P<ip_address>.*)\): icmp_seq=(?P<icmp_sequence>\d*) ttl=(?P<time_to_live>\d*) time=("
    r"?P<time>.*) (?P<time_unit>.*)"
)


LATENCY_ERRORS = {
    "ping-err": "ping had an unknown error",
    "ping-split": "ping attempted to split the result but it was in an unanticipated format",
    "ping-regex": "ping attempted get the known regex format and failed.",
    "ping-minimum-latency": "ping could not process the minimum latency.",
    "ping-maximum-latency": "ping could not process the maximum latency.",
    "ping-average-latency": "ping could not process the average latency.",
    "ping-median-deviation": "ping could not process the median deviation.",
    "ping-no-server": "No closest server could be resolved.",
    "ping-timeout": "Measurement request timed out.",
}


class LatencyMeasurement(BaseMeasurement):
    def __init__(self, id, host, count=4, include_individual_results=False):
        super(LatencyMeasurement, self).__init__(id=id)
        if count < 1:
            raise ValueError(
                "A value of {count} was provided for the number of pings. This must be a positive "
                "integer greater than 0.".format(count=count)
            )

        validated_domain = validators.domain(host)
        validated_ip = validators.ipv4(host)
        if isinstance(validated_domain, ValidationFailure) & isinstance(
            validated_ip, ValidationFailure
        ):
            raise ValueError("`{host}` is not a valid host".format(host=host))

        self.host = host
        self.count = count
        self.include_individual_results = include_individual_results

    def measure(self):
        return self._get_latency_results(
            self.host,
            count=self.count,
            include_individual_results=self.include_individual_results,
        )

    def _get_latency_results(  # noqa: C901
        self, host, count=4, include_individual_results=False
    ):
        """Perform the latency measurement.

        :param host: The host name to perform the test against.
        :param count: The number of pings to determine latency with.
        :param include_individual_results: Should each of the
        individualised ping iterations be included in the results?
        :return: A list of `LatencyMeasurementResult` and
        `LatencyIndividualMeasurementResult` if individual results are
        enabled.
        """
        if host is None:
            return [self._get_latency_error("ping-no-server", host, traceback=None)]

        latency_out = subprocess.run(
            ["ping", "-c", "{c}".format(c=count), "{h}".format(h=host)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        # Note: only this error cares about stderr, other issues will be evident in stdout
        if latency_out.returncode != 0:
            return [
                self._get_latency_error("ping-err", host, traceback=latency_out.stderr)
            ]

        try:
            latency_data = latency_out.stdout.split("\n")[-2]
        except IndexError:
            return [
                self._get_latency_error(
                    "ping-split", host, traceback=latency_out.stdout
                )
            ]

        matches = LATENCY_OUTPUT_REGEX.search(latency_data)
        try:
            match_data = matches.groupdict()
        except AttributeError:
            return [
                self._get_latency_error(
                    "ping-regex", host, traceback=latency_out.stdout
                )
            ]

        if len(match_data.keys()) != 4:
            return [
                self._get_latency_error(
                    "ping-regex", host, traceback=latency_out.stdout
                )
            ]
        match_data = matches.groupdict()

        try:
            maximum_latency = float(match_data.get("maximum_latency"))
        except (TypeError, ValueError):
            return [
                self._get_latency_error(
                    "ping-maximum-latency", host, traceback=latency_out.stdout
                )
            ]

        try:
            minimum_latency = float(match_data.get("minimum_latency"))
        except (TypeError, ValueError):
            return [
                self._get_latency_error(
                    "ping-minimum-latency", host, traceback=latency_out.stdout
                )
            ]

        try:
            average_latency = float(match_data.get("average_latency"))
        except (TypeError, ValueError):
            return [
                self._get_latency_error(
                    "ping-average-latency", host, traceback=latency_out.stdout
                )
            ]

        try:
            median_deviation = float(match_data.get("median_deviation"))
        except (TypeError, ValueError):
            return [
                self._get_latency_error(
                    "ping-median_deviation", host, traceback=latency_out.stdout
                )
            ]

        try:
            latency_data = latency_out.stdout.split("\n")[-3]
        except IndexError:
            return [
                self._get_latency_error(
                    "ping-split", host, traceback=latency_out.stdout
                )
            ]

        matches = LATENCY_PACKETS_REGEX.search(latency_data)
        try:
            match_data = matches.groupdict()
        except AttributeError:
            return [
                self._get_latency_error(
                    "ping-regex", host, traceback=latency_out.stdout
                )
            ]

        packets_transmitted = int(match_data.get("packets_transmitted"))
        packets_received = int(match_data.get("packets_received"))
        packet_loss = float(match_data.get("packet_loss"))
        elapsed_time = float(match_data.get("time"))
        elapsed_time_unit = match_data.get("time_unit")

        results = [
            LatencyMeasurementResult(
                id=self.id,
                host=host,
                minimum_latency=minimum_latency,
                average_latency=average_latency,
                maximum_latency=maximum_latency,
                median_deviation=median_deviation,
                packets_transmitted=packets_transmitted,
                packets_received=packets_received,
                packets_lost=packet_loss,
                packets_lost_unit=RatioUnit.percentage,
                elapsed_time=elapsed_time,
                elapsed_time_unit=TimeUnit(elapsed_time_unit),
                errors=[],
            )
        ]

        if include_individual_results:
            matches = LATENCY_INDIVIDUAL_PING_REGEX.findall(latency_out.stdout)
            for match in matches:
                results.append(
                    LatencyIndividualMeasurementResult(
                        id=self.id,
                        host=host,
                        errors=[],
                        packet_size=match[0],
                        packet_size_unit=StorageUnit(match[1].replace("bytes", "B")),
                        reverse_dns_address=match[2],
                        ip_address=match[3],
                        icmp_sequence=match[4],
                        time_to_live=match[5],
                        elapsed_time=match[6],
                        elapsed_time_unit=TimeUnit(match[7]),
                    )
                )

        return results

    def _get_latency_error(self, key, host, traceback):
        return LatencyMeasurementResult(
            id=self.id,
            host=host,
            minimum_latency=None,
            average_latency=None,
            maximum_latency=None,
            median_deviation=None,
            packets_transmitted=None,
            packets_received=None,
            packets_lost=None,
            packets_lost_unit=None,
            elapsed_time=None,
            elapsed_time_unit=None,
            errors=[
                Error(
                    key=key,
                    description=LATENCY_ERRORS.get(key, ""),
                    traceback=traceback,
                )
            ],
        )
