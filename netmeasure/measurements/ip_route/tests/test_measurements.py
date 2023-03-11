import socket
from unittest import TestCase, mock

from netmeasure.measurements.ip_route.measurements import (
    IPRouteMeasurement,
    ROUTE_ERRORS,
)
from netmeasure.measurements.latency.measurements import LatencyMeasurement
from netmeasure.measurements.ip_route.results import IPRouteMeasurementResult
from netmeasure.measurements.latency.results import LatencyMeasurementResult
from netmeasure.measurements.base.results import Error
from netmeasure.units import RatioUnit, TimeUnit, StorageUnit, NetworkUnit


class IPRouteTestCase(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        super().setUp()
        self.id = "1"
        self.example_hosts_one = ["www.fakesitetwo.com"]
        self.example_hosts_three = [
            "www.fakesiteone.com",
            "www.fakesitetwo.com",
            "www.fakesitethree.com",
        ]
        self.iprm = IPRouteMeasurement(self.id, hosts=self.example_hosts_one, count=4)
        self.example_trace_five = {
            "final.ip": {
                1: ("first.ip", False),
                2: ("second.ip", False),
                3: ("third.ip", False),
                4: ("fourth.ip", False),
                5: ("final.ip", True),
            }
        }
        self.example_trace_five_list = [
            "first.ip",
            "second.ip",
            "third.ip",
            "fourth.ip",
            "final.ip",
        ]
        self.example_result_five = IPRouteMeasurementResult(
            id=self.id,
            host=self.example_hosts_one[0],
            hop_count=5,
            ip="final.ip",
            route=self.example_trace_five_list,
            errors=[],
        )
        self.example_result_permission_err = IPRouteMeasurementResult(
            id=self.id,
            host=None,
            hop_count=None,
            ip=None,
            route=None,
            errors=[
                Error(
                    key="route-permission",
                    description=ROUTE_ERRORS.get("route-permission", ""),
                    traceback="[Errno 1] Operation not permitted",
                )
            ],
        )
        self.example_result_address_err = IPRouteMeasurementResult(
            id=self.id,
            host=None,
            hop_count=None,
            ip=None,
            route=None,
            errors=[
                Error(
                    key="route-address",
                    description=ROUTE_ERRORS.get("route-address", ""),
                    traceback="[Errno -2] Name or service not known",
                )
            ],
        )
        self.example_latency_results_three = [
            (
                LatencyMeasurementResult(
                    id=self.id,
                    host="www.fakesiteone.com",
                    minimum_latency=None,
                    average_latency=None,
                    maximum_latency=None,
                    median_deviation=None,
                    errors=[],
                    packets_transmitted=None,
                    packets_received=None,
                    packets_lost=None,
                    packets_lost_unit=None,
                    elapsed_time=None,
                    elapsed_time_unit=None,
                ),
            ),
            (
                LatencyMeasurementResult(
                    id=self.id,
                    host="www.fakesitetwo.com",
                    minimum_latency=None,
                    average_latency=25.0,
                    maximum_latency=None,
                    median_deviation=None,
                    errors=[],
                    packets_transmitted=None,
                    packets_received=None,
                    packets_lost=None,
                    packets_lost_unit=None,
                    elapsed_time=None,
                    elapsed_time_unit=None,
                ),
            ),
            (
                LatencyMeasurementResult(
                    id=self.id,
                    host="www.fakesitethree.com",
                    minimum_latency=None,
                    average_latency=999.0,
                    maximum_latency=None,
                    median_deviation=None,
                    errors=[],
                    packets_transmitted=None,
                    packets_received=None,
                    packets_lost=None,
                    packets_lost_unit=None,
                    elapsed_time=None,
                    elapsed_time_unit=None,
                ),
            ),
        ]
        self.example_least_latent_result = (
            (
                LatencyMeasurementResult(
                    id=self.id,
                    host="www.fakesitetwo.com",
                    minimum_latency=None,
                    average_latency=24.9,
                    maximum_latency=None,
                    median_deviation=None,
                    errors=[],
                    packets_transmitted=None,
                    packets_received=None,
                    packets_lost=None,
                    packets_lost_unit=None,
                    elapsed_time=None,
                    elapsed_time_unit=None,
                ),
            ),
        )

    @mock.patch.object(socket, "socket")
    @mock.patch.object(LatencyMeasurement, "measure")
    @mock.patch("scapy.layers.inet.traceroute")
    def test_measure(self, mock_get_traceroute, mock_latency_results, mock_socket):
        iprm_three = IPRouteMeasurement(
            self.id, hosts=self.example_hosts_three, count=4
        )
        mock_trace = mock.MagicMock()
        mock_trace.get_trace.return_value = self.example_trace_five
        mock_get_traceroute.return_value = [mock_trace, None]
        mock_latency_results.side_effect = [
            self.example_latency_results_three[0],
            self.example_latency_results_three[1],
            self.example_latency_results_three[2],
            self.example_least_latent_result,
        ]
        self.assertEqual(
            iprm_three.measure(),
            [
                self.example_result_five,
                self.example_least_latent_result[0],
                self.example_latency_results_three[1][0],
                self.example_latency_results_three[2][0],
                self.example_latency_results_three[0][0],
            ],
        )

    @mock.patch.object(socket, "socket")
    @mock.patch("scapy.layers.inet.traceroute")
    def test_get_trace_five(self, mock_get_traceroute, mock_socket):
        mock_trace = mock.MagicMock()
        mock_trace.get_trace.return_value = self.example_trace_five
        mock_get_traceroute.return_value = [mock_trace, None]
        self.assertEqual(
            self.iprm._get_traceroute_result(self.example_hosts_one[0]),
            self.example_result_five,
        )

    @mock.patch.object(socket, "socket")
    @mock.patch("scapy.layers.inet.traceroute")
    def test_get_trace_permission_err(self, mock_get_traceroute, mock_socket):
        mock_get_traceroute.side_effect = PermissionError(
            "[Errno 1] Operation not permitted"
        )
        self.assertEqual(
            self.iprm._get_traceroute_result(self.example_hosts_one[0]),
            self.example_result_permission_err,
        )

    @mock.patch.object(socket, "socket")
    @mock.patch("scapy.layers.inet.traceroute")
    def test_get_trace_address_err(self, mock_get_traceroute, mock_socket):
        mock_get_traceroute.side_effect = socket.gaierror(
            "[Errno -2] Name or service not known"
        )
        self.assertEqual(
            self.iprm._get_traceroute_result(self.example_hosts_one[0]),
            self.example_result_address_err,
        )


class IPRouteMeasurementLeastLatentTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.id = "1"
        self.example_hosts_three = [
            "www.fakesiteone.com",
            "www.fakesitetwo.com",
            "www.fakesitethree.com",
        ]
        self.example_results_three = [
            (
                LatencyMeasurementResult(
                    id=self.id,
                    host="www.fakesiteone.com",
                    minimum_latency=None,
                    average_latency=None,
                    maximum_latency=None,
                    median_deviation=None,
                    errors=[],
                    packets_transmitted=None,
                    packets_received=None,
                    packets_lost=None,
                    packets_lost_unit=None,
                    elapsed_time=None,
                    elapsed_time_unit=None,
                ),
            ),
            (
                LatencyMeasurementResult(
                    id=self.id,
                    host="www.fakesitetwo.com",
                    minimum_latency=None,
                    average_latency=25.0,
                    maximum_latency=None,
                    median_deviation=None,
                    errors=[],
                    packets_transmitted=None,
                    packets_received=None,
                    packets_lost=None,
                    packets_lost_unit=None,
                    elapsed_time=None,
                    elapsed_time_unit=None,
                ),
            ),
            (
                LatencyMeasurementResult(
                    id=self.id,
                    host="www.fakesitethree.com",
                    minimum_latency=None,
                    average_latency=999.0,
                    maximum_latency=None,
                    median_deviation=None,
                    errors=[],
                    packets_transmitted=None,
                    packets_received=None,
                    packets_lost=None,
                    packets_lost_unit=None,
                    elapsed_time=None,
                    elapsed_time_unit=None,
                ),
            ),
        ]
        self.example_hosts_one = ["www.fakesiteone.com"]
        self.example_results_one = [
            LatencyMeasurementResult(
                id=self.id,
                host="www.fakesiteone.com",
                minimum_latency=None,
                average_latency=None,
                maximum_latency=None,
                median_deviation=None,
                errors=[],
                packets_transmitted=None,
                packets_received=None,
                packets_lost=None,
                packets_lost_unit=None,
                elapsed_time=None,
                elapsed_time_unit=None,
            ),
        ]
        self.iprm_three = IPRouteMeasurement(
            self.id, hosts=self.example_hosts_three, count=4
        )
        self.iprm_one = IPRouteMeasurement(
            self.id, hosts=self.example_hosts_three, count=4
        )

    @mock.patch.object(LatencyMeasurement, "measure")
    def test_sort_least_latent_host(self, mock_latency_results):
        mock_latency_results.side_effect = self.example_results_three
        self.assertEqual(
            self.iprm_three._find_least_latent_host(self.example_hosts_three),
            [
                (self.example_hosts_three[1], self.example_results_three[1][0]),
                (self.example_hosts_three[2], self.example_results_three[2][0]),
                (self.example_hosts_three[0], self.example_results_three[0][0]),
            ],
        )

    @mock.patch.object(LatencyMeasurement, "measure")
    def test_sort_one_host(self, mock_latency_results):
        mock_latency_results.return_value = self.example_results_one
        self.assertEqual(
            self.iprm_one._find_least_latent_host(self.example_hosts_one),
            [(self.example_hosts_one[0], self.example_results_one[0])],
        )


class IPRouteMeasurementCreationTestCase(TestCase):
    def test_invalid_hosts(self, *args):
        self.assertRaises(ValueError, IPRouteMeasurement, "test", ["invalid..host"])

    def test_invalid_count(self, *args):
        self.assertRaises(
            TypeError,
            IPRouteMeasurement,
            "test",
            ["validfakeurl.com"],
            count="invalid-count",
        )

    def test_invalid_negative_count(self, *args):
        self.assertRaises(
            ValueError, IPRouteMeasurement, "test", ["validfakeurl.com"], count=-2
        )

    def test_valid_ip_host(self):
        IPRouteMeasurement("test", ["1.1.1.1"])
