import subprocess
from unittest import TestCase, mock

from netmeasure.measurements.latency.measurements import (
    LatencyMeasurement,
    LATENCY_ERRORS,
)
from netmeasure.measurements.latency.results import (
    LatencyMeasurementResult,
    LatencyIndividualMeasurementResult,
)
from netmeasure.measurements.base.results import Error
from netmeasure.units import RatioUnit, TimeUnit, StorageUnit


class FileDownloadMeasurementLatencyTestCase(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        super().setUp()
        self.measurement = LatencyMeasurement("test", "validfakehost.com")
        self.valid_latency = LatencyMeasurementResult(
            id="test",
            host="validfakehost.com",
            minimum_latency=6.211,
            average_latency=6.617,
            maximum_latency=7.069,
            median_deviation=0.315,
            errors=[],
            packets_transmitted=4,
            packets_received=4,
            packets_lost=0.0,
            packets_lost_unit=RatioUnit.percentage,
            elapsed_time=7.0,
            elapsed_time_unit=TimeUnit.millisecond,
        )
        self.invalid_latency = LatencyMeasurementResult(
            id="test",
            host="validfakehost.com",
            minimum_latency=None,
            average_latency=None,
            maximum_latency=None,
            median_deviation=None,
            errors=[
                Error(
                    key="ping-err",
                    description=LATENCY_ERRORS.get("ping-err", ""),
                    traceback="the ping messed up!",
                )
            ],
            packets_transmitted=None,
            packets_received=None,
            packets_lost=None,
            packets_lost_unit=None,
            elapsed_time=None,
            elapsed_time_unit=None,
        )
        self.invalid_regex = LatencyMeasurementResult(
            id="test",
            host="validfakehost.com",
            minimum_latency=None,
            average_latency=None,
            maximum_latency=None,
            median_deviation=None,
            errors=[
                Error(
                    key="ping-regex",
                    description=LATENCY_ERRORS.get("ping-regex", ""),
                    traceback="\nrtt min/avg/max/mdev = [BAD REGEX] ms\n",
                )
            ],
            packets_transmitted=None,
            packets_received=None,
            packets_lost=None,
            packets_lost_unit=None,
            elapsed_time=None,
            elapsed_time_unit=None,
        )

    @mock.patch("subprocess.run")
    def test_valid_latency(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="PING www.google.com (216.58.199.36) 56(84) bytes of data.\n64 bytes from syd09s12-in-f4.1e100.net (216.58.199.36): icmp_seq=1 ttl=55 time=7.07 ms\n64 bytes from syd09s12-in-f4.1e100.net (216.58.199.36): icmp_seq=2 ttl=55 time=6.68 ms\n64 bytes from syd09s12-in-f4.1e100.net (216.58.199.36): icmp_seq=3 ttl=55 time=6.21 ms\n64 bytes from syd09s12-in-f4.1e100.net (216.58.199.36): icmp_seq=4 ttl=55 time=6.51 ms\n\n--- www.google.com ping statistics ---\n4 packets transmitted, 4 received, 0% packet loss, time 7ms\nrtt min/avg/max/mdev = 6.211/6.617/7.069/0.315 ms\n",
            stderr="",
        )
        self.assertEqual(
            self.valid_latency,
            self.measurement._get_latency_results("validfakehost.com")[0],
        )

    @mock.patch("subprocess.run")
    def test_valid_detailed_latency(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="PING www.google.com (216.58.199.36) 56(84) bytes of data.\n64 bytes from syd09s12-in-f4.1e100.net (216.58.199.36): icmp_seq=1 ttl=55 time=7.07 ms\n64 bytes from syd09s12-in-f4.1e100.net (216.58.199.36): icmp_seq=2 ttl=55 time=6.68 ms\n64 bytes from syd09s12-in-f4.1e100.net (216.58.199.36): icmp_seq=3 ttl=55 time=6.21 ms\n64 bytes from syd09s12-in-f4.1e100.net (216.58.199.36): icmp_seq=4 ttl=55 time=6.51 ms\n\n--- www.google.com ping statistics ---\n4 packets transmitted, 4 received, 0% packet loss, time 7ms\nrtt min/avg/max/mdev = 6.211/6.617/7.069/0.315 ms\n",
            stderr="",
        )
        measurement = LatencyMeasurement(
            "test", "validfakehost.com", include_individual_results=True
        )
        self.assertEqual(
            [
                self.valid_latency,
                LatencyIndividualMeasurementResult(
                    id="test",
                    errors=[],
                    host="validfakehost.com",
                    packet_size="64",
                    packet_size_unit=StorageUnit.byte,
                    reverse_dns_address="syd09s12-in-f4.1e100.net",
                    ip_address="216.58.199.36",
                    icmp_sequence="1",
                    time_to_live="55",
                    elapsed_time="7.07",
                    elapsed_time_unit=TimeUnit.millisecond,
                ),
                LatencyIndividualMeasurementResult(
                    id="test",
                    errors=[],
                    host="validfakehost.com",
                    packet_size="64",
                    packet_size_unit=StorageUnit.byte,
                    reverse_dns_address="syd09s12-in-f4.1e100.net",
                    ip_address="216.58.199.36",
                    icmp_sequence="2",
                    time_to_live="55",
                    elapsed_time="6.68",
                    elapsed_time_unit=TimeUnit.millisecond,
                ),
                LatencyIndividualMeasurementResult(
                    id="test",
                    errors=[],
                    host="validfakehost.com",
                    packet_size="64",
                    packet_size_unit=StorageUnit.byte,
                    reverse_dns_address="syd09s12-in-f4.1e100.net",
                    ip_address="216.58.199.36",
                    icmp_sequence="3",
                    time_to_live="55",
                    elapsed_time="6.21",
                    elapsed_time_unit=TimeUnit.millisecond,
                ),
                LatencyIndividualMeasurementResult(
                    id="test",
                    errors=[],
                    host="validfakehost.com",
                    packet_size="64",
                    packet_size_unit=StorageUnit.byte,
                    reverse_dns_address="syd09s12-in-f4.1e100.net",
                    ip_address="216.58.199.36",
                    icmp_sequence="4",
                    time_to_live="55",
                    elapsed_time="6.51",
                    elapsed_time_unit=TimeUnit.millisecond,
                ),
            ],
            measurement._get_latency_results(
                "validfakehost.com", include_individual_results=True
            ),
        )

    @mock.patch("subprocess.run")
    def test_invalid_latency(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="\nrtt min/avg/max/mdev = 5.484/6.133/7.133/0.611 ms\n",
            stderr="the ping messed up!",
        )
        self.assertEqual(
            self.invalid_latency,
            self.measurement._get_latency_results("validfakehost.com")[0],
        )

    @mock.patch("subprocess.run")
    def test_latency_invalid_regex(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="\nrtt min/avg/max/mdev = [BAD REGEX] ms\n",
            stderr="",
        )
        self.assertEqual(
            self.invalid_regex,
            self.measurement._get_latency_results("validfakehost.com")[0],
        )

    def test_host_is_none_returns_error(self):
        self.assertEqual(
            self.measurement._get_latency_results(None),
            [
                LatencyMeasurementResult(
                    id="test",
                    errors=[
                        Error(
                            key="ping-no-server",
                            description="No closest server could be resolved.",
                            traceback=None,
                        )
                    ],
                    host=None,
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
                )
            ],
        )


class LatencyMeasurementInitTestCase(TestCase):
    def test_init_sets_values(self):
        latency_measurement = LatencyMeasurement(
            "test", "test.com", count=6, include_individual_results=True
        )

        self.assertEqual(latency_measurement.id, "test")
        self.assertEqual(latency_measurement.host, "test.com")
        self.assertEqual(latency_measurement.count, 6)
        self.assertEqual(latency_measurement.include_individual_results, True)

    def test_count_less_than_1_produces_error(self):
        with self.assertRaises(ValueError):
            LatencyMeasurement("test", "test.com", count=0)

    def test_invalid_host_gets_raised(self):
        with self.assertRaises(ValueError):
            LatencyMeasurement("test", "%test")

    def test_valid_ip_host(self):
        LatencyMeasurement("test", "1.1.1.1")
