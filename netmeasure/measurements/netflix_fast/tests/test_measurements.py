import subprocess
import sys
import json
from unittest import TestCase, mock
from threading import active_count
from itertools import cycle

from netmeasure.measurements.netflix_fast.measurements import (
    NetflixFastMeasurement,
    NETFLIX_ERRORS,
    MIN_TIME_SECONDS,
    PING_COUNT,
    MEASUREMENTS_COUNTED_BEFORE_CONSIDERED_STABLE,
    STABLE_MEASUREMENTS_DELTA,
)
from netmeasure.measurements.netflix_fast.results import (
    NetflixFastMeasurementResult,
    NetflixFastThreadResult,
)
from netmeasure.measurements.latency.results import LatencyMeasurementResult
from netmeasure.measurements.base.results import Error
from netmeasure.units import RatioUnit, TimeUnit, StorageUnit, NetworkUnit


"""
Note that calling .measure() and ._get_fast_result() mutate the NetflixFastMeasurement object.
As a result these objects should preferably be created inside the test function if these functions are to be called.
"""


class NetflixResultTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.nft = NetflixFastMeasurement(
            "1", urlcount=3, terminate_on_thread_complete=True
        )
        self.api_response_three = {
            "client": {
                "location": {"city": "HBox City", "country": "HBoxtopia"},
                "isp": "ServiceProvider",
                "asn": "0000",
                "ip": "0000:0000:000a:0000:0c00:0b00:a0a0:f0f0",
            },
            "targets": [
                {
                    "location": {
                        "city": "Foreign City One",
                        "country": "Foreign Country One",
                    },
                    "name": "https://afakeurl.1.notreal.net/speedtest",
                    "url": "https://afakeurl.1.notreal.net/speedtest",
                },
                {
                    "location": {
                        "city": "Foreign City Two",
                        "country": "Foreign Country Two",
                    },
                    "name": "https://afakeurl.2.notreal.net/speedtest",
                    "url": "https://afakeurl.2.notreal.net/speedtest",
                },
                {
                    "location": {
                        "city": "Foreign City Three",
                        "country": "Foreign Country Three",
                    },
                    "name": "https://afakeurl.3.notreal.net/speedtest",
                    "url": "https://afakeurl.3.notreal.net/speedtest",
                },
            ],
        }
        self.fast_data_three = {
            "speed_bits": 1234,
            "total": 4321,
            "reason_terminated": "fake_reason",
        }
        self.fast_result_three = NetflixFastMeasurementResult(
            id="1",
            download_rate=float(self.fast_data_three["speed_bits"]),
            download_rate_unit=NetworkUnit("bit/s"),
            download_size=float(self.fast_data_three["total"]),
            download_size_unit=StorageUnit("B"),
            asn=self.api_response_three["client"]["asn"],
            ip=self.api_response_three["client"]["ip"],
            isp=self.api_response_three["client"]["isp"],
            city=self.api_response_three["client"]["location"]["city"],
            country=self.api_response_three["client"]["location"]["country"],
            urlcount=3,
            reason_terminated=self.fast_data_three["reason_terminated"],
            errors=[],
        )
        self.thread_result_three_list = [
            [
                NetflixFastThreadResult(
                    id="1",
                    host="afakeurl.1.notreal.net",
                    city=self.api_response_three["targets"][0]["location"]["city"],
                    country=self.api_response_three["targets"][0]["location"][
                        "country"
                    ],
                    download_size=0,
                    download_size_unit=StorageUnit("B"),
                    download_rate=0,
                    download_rate_unit=NetworkUnit("bit/s"),
                    elapsed_time=0,
                    elapsed_time_unit=TimeUnit("s"),
                    errors=[],
                ),
                LatencyMeasurementResult(
                    id="1",
                    host="afakeurl.1.notreal.net",
                    minimum_latency=0,
                    average_latency=0,
                    maximum_latency=0,
                    median_deviation=0,
                    packets_transmitted=0,
                    packets_received=0,
                    packets_lost=0,
                    packets_lost_unit=RatioUnit("%"),
                    elapsed_time=0,
                    elapsed_time_unit=TimeUnit("d"),
                    errors=[],
                ),
            ],
            [
                NetflixFastThreadResult(
                    id="1",
                    host="afakeurl.1.notreal.net",
                    city=self.api_response_three["targets"][1]["location"]["city"],
                    country=self.api_response_three["targets"][1]["location"][
                        "country"
                    ],
                    download_size=0,
                    download_size_unit=StorageUnit("B"),
                    download_rate=0,
                    download_rate_unit=NetworkUnit("bit/s"),
                    elapsed_time=0,
                    elapsed_time_unit=TimeUnit("s"),
                    errors=[],
                ),
                LatencyMeasurementResult(
                    id="1",
                    host="afakeurl.1.notreal.net",
                    minimum_latency=0,
                    average_latency=0,
                    maximum_latency=0,
                    median_deviation=0,
                    packets_transmitted=0,
                    packets_received=0,
                    packets_lost=0,
                    packets_lost_unit=RatioUnit("%"),
                    elapsed_time=0,
                    elapsed_time_unit=TimeUnit("d"),
                    errors=[],
                ),
            ],
            [
                NetflixFastThreadResult(
                    id="1",
                    host="afakeurl.1.notreal.net",
                    city=self.api_response_three["targets"][2]["location"]["city"],
                    country=self.api_response_three["targets"][2]["location"][
                        "country"
                    ],
                    download_size=0,
                    download_size_unit=StorageUnit("B"),
                    download_rate=0,
                    download_rate_unit=NetworkUnit("bit/s"),
                    elapsed_time=0,
                    elapsed_time_unit=TimeUnit("s"),
                    errors=[],
                ),
                LatencyMeasurementResult(
                    id="1",
                    host="afakeurl.1.notreal.net",
                    minimum_latency=0,
                    average_latency=0,
                    maximum_latency=0,
                    median_deviation=0,
                    packets_transmitted=0,
                    packets_received=0,
                    packets_lost=0,
                    packets_lost_unit=RatioUnit("%"),
                    elapsed_time=0,
                    elapsed_time_unit=TimeUnit("d"),
                    errors=[],
                ),
            ],
        ]

    @mock.patch(
        "netmeasure.measurements.netflix_fast.measurements.NetflixFastMeasurement._get_fast_result"
    )
    @mock.patch(
        "netmeasure.measurements.netflix_fast.measurements.NetflixFastMeasurement._get_url_result"
    )
    def test_measure(self, mock_get_url_result, mock_get_fast_result):
        mock_get_url_result.side_effect = self.thread_result_three_list
        mock_get_fast_result.return_value = self.fast_result_three
        assert self.nft.measure() == (
            [self.fast_result_three]
            + self.thread_result_three_list[0]
            + self.thread_result_three_list[1]
            + self.thread_result_three_list[2]
        )

    @mock.patch(
        "netmeasure.measurements.netflix_fast.measurements.NetflixFastMeasurement._manage_threads"
    )
    @mock.patch(
        "netmeasure.measurements.netflix_fast.measurements.NetflixFastMeasurement._get_connection"
    )
    @mock.patch("requests.Session")
    def test_fast_result(
        self, mock_get_session, mock_get_connection, mock_manage_threads
    ):
        mock_session = mock.MagicMock()
        mock_resp = mock.MagicMock()
        mock_resp.text = '<script src="(This is the script)">'
        mock_script_resp = mock.MagicMock()
        mock_script_resp.text = (
            'This is the script response, containing token:"This is the token"'
        )
        mock_api_resp = mock.MagicMock()
        mock_api_resp.json.return_value = self.api_response_three
        mock_session.get.side_effect = [mock_resp, mock_script_resp, mock_api_resp]
        mock_get_session.return_value = mock_session
        mock_manage_threads.return_value = self.fast_data_three
        self.nft.thread_results = [
            {
                "index": i,
                "elapsed_time": None,
                "download_size": 0,
                "download_rate": 0,
                "url": None,
                "location": None,
            }
            for i in range(self.nft.urlcount)  # Generate thread results dict structure
        ]

        assert self.nft._get_fast_result() == self.fast_result_three

    @mock.patch(
        "netmeasure.measurements.netflix_fast.measurements.NetflixFastMeasurement._manage_threads"
    )
    @mock.patch(
        "netmeasure.measurements.netflix_fast.measurements.NetflixFastMeasurement._get_connection"
    )
    @mock.patch(
        "netmeasure.measurements.netflix_fast.measurements.NetflixFastMeasurement._query_api"
    )
    @mock.patch("requests.Session")
    def test_fast_result_client_data(
        self, mock_get_session, mock_query_api, mock_get_connection, mock_manage_threads
    ):
        assert True

    # def test_thread_adding_terminating(self):
    #     nft = NetflixFastMeasurement("1", urlcount=5, terminate_on_thread_complete=True)
    #     conns = []
    #     for i in range(1,10):
    #         m = mock.MagicMock()
    #         m.iter_content.return_value = ["BYTES" for iter in range(i)]
    #         conns.append(m)
    #     x = nft._manage_threads(conns)
    #     assert ((x["reason_terminated"] == "thread_complete"))

    def test_thread_adding_all_complete(self):
        nft = NetflixFastMeasurement(
            "1", urlcount=5, terminate_on_thread_complete=False
        )
        conns = []
        for i in range(1, 6):
            m = mock.MagicMock()
            m.iter_content.return_value = ["BYTES" for iter in range(i)]
            conns.append(m)
        nft.thread_results = [
            {
                "index": i,
                "elapsed_time": None,
                "download_size": 0,
                "download_rate": 0,
                "url": None,
                "location": None,
            }
            for i in range(nft.urlcount)  # Generate thread results dict structure
        ]
        x = nft._manage_threads(conns)
        assert (x["reason_terminated"] == "all_complete") & (x["total"] == 75)

    @mock.patch(
        "netmeasure.measurements.netflix_fast.measurements.NetflixFastMeasurement._is_stabilised"
    )
    def test_thread_adding_stabilised(self, mock_is_stabilised):
        mock_is_stabilised.return_value = True
        nft = NetflixFastMeasurement(
            "1",
            urlcount=5,
            terminate_on_thread_complete=False,
            terminate_on_result_stable=True,
        )
        conns = []
        for i in range(1, 6):
            m = mock.MagicMock()
            m.iter_content.return_value = ["BYTES" for _ in range(i)]
            conns.append(m)
        x = nft._manage_threads(conns)
        assert x["reason_terminated"] == "result_stabilised"

    @mock.patch(
        "netmeasure.measurements.latency.measurements.LatencyMeasurement.measure"
    )
    def test_latency_result(self, mock_latency_measure):
        mock_latency_result = LatencyMeasurementResult(
            id=("1"),
            host="afakeurl.1.notreal.net",
            minimum_latency=0,
            average_latency=0,
            maximum_latency=0,
            median_deviation=0,
            packets_transmitted=0,
            packets_received=0,
            packets_lost=0,
            packets_lost_unit=RatioUnit("%"),
            elapsed_time=0,
            elapsed_time_unit=TimeUnit("d"),
            errors=[],
        )
        mock_latency_measure.return_value = [mock_latency_result]
        mock_thread_result = {
            "url": "https://afakeurl.1.notreal.net/speedtest",
            "location": {"city": "Foreign City One", "country": "Foreign Country One"},
            "download_size": 0,
            "download_rate": 0,
            "elapsed_time": 0,
        }
        assert (
            self.nft._get_url_result(mock_thread_result)
            == self.thread_result_three_list[0]
        )


class HelperFunctionTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.nft = NetflixFastMeasurement("1")

    @mock.patch("requests.Session")
    def test_get_connection(self, mock_get_session):
        mock_session = mock.MagicMock()
        mock_session.get.side_effect = ["first_url", "second_url", "third_url"]
        mock_get_session.return_value = mock_session
        nft = NetflixFastMeasurement("1")
        assert [
            nft._get_connection("first"),
            nft._get_connection("second"),
            nft._get_connection("third"),
        ] == ["first_url", "second_url", "third_url"]
        assert len(nft.sessions) == 3

    def test_is_stabilised_is_stable(self):
        mock_elapsed_time = MIN_TIME_SECONDS + 1
        mock_percent_deltas = [
            STABLE_MEASUREMENTS_DELTA - sys.float_info.epsilon
        ] * MEASUREMENTS_COUNTED_BEFORE_CONSIDERED_STABLE
        assert self.nft._is_stabilised(mock_percent_deltas, mock_elapsed_time) is True

    def test_is_stabilised_not_stable(self):
        mock_elapsed_time = MIN_TIME_SECONDS + 1
        mock_percent_deltas = [STABLE_MEASUREMENTS_DELTA - sys.float_info.epsilon] * (
            MEASUREMENTS_COUNTED_BEFORE_CONSIDERED_STABLE - 1
        )
        mock_percent_deltas.append(STABLE_MEASUREMENTS_DELTA + sys.float_info.epsilon)
        assert self.nft._is_stabilised(mock_percent_deltas, mock_elapsed_time) is False

    def test_is_stabilised_too_short(self):
        mock_elapsed_time = MIN_TIME_SECONDS + 1
        mock_percent_deltas = [STABLE_MEASUREMENTS_DELTA - sys.float_info.epsilon] * (
            MEASUREMENTS_COUNTED_BEFORE_CONSIDERED_STABLE - 1
        )
        assert self.nft._is_stabilised(mock_percent_deltas, mock_elapsed_time) is False

    def test_is_stabilised_too_early(self):
        mock_elapsed_time = MIN_TIME_SECONDS - 1
        mock_percent_deltas = [
            STABLE_MEASUREMENTS_DELTA - sys.float_info.epsilon
        ] * MEASUREMENTS_COUNTED_BEFORE_CONSIDERED_STABLE
        assert self.nft._is_stabilised(mock_percent_deltas, mock_elapsed_time) is False


class ErrorsTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.nft = NetflixFastMeasurement("1")

    @mock.patch("requests.Session")
    def test_netflix_response_err(self, mock_get_session):
        mock_error_result = NetflixFastMeasurementResult(
            id=("1"),
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            asn=None,
            ip=None,
            isp=None,
            city=None,
            country=None,
            urlcount=self.nft.urlcount,
            reason_terminated=None,
            errors=[
                Error(
                    key="netflix-response",
                    description=NETFLIX_ERRORS.get("netflix-response", ""),
                    traceback="Failed to pretend to establish a new connection",
                )
            ],
        )
        mock_session = mock.MagicMock()
        mock_session.get.side_effect = [
            ConnectionError("Failed to pretend to establish a new connection")
        ]
        mock_get_session.return_value = mock_session
        assert self.nft._get_fast_result() == mock_error_result

    @mock.patch("requests.Session")
    def test_netflix_regex_err(self, mock_get_session):
        mock_error_result = NetflixFastMeasurementResult(
            id=("1"),
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            asn=None,
            ip=None,
            isp=None,
            city=None,
            country=None,
            urlcount=self.nft.urlcount,
            reason_terminated=None,
            errors=[
                Error(
                    key="netflix-script-regex",
                    description=NETFLIX_ERRORS.get("netflix-script-regex", ""),
                    traceback='<Bript Brc="(This should be impossible to find)">',
                )
            ],
        )
        mock_session = mock.MagicMock()
        mock_resp = mock.MagicMock()
        mock_resp.text = '<Bript Brc="(This should be impossible to find)">'
        mock_session.get.side_effect = [mock_resp]
        mock_get_session.return_value = mock_session
        assert self.nft._get_fast_result() == mock_error_result

    @mock.patch("requests.Session")
    def test_netflix_script_response_err(self, mock_get_session):
        mock_error_result = NetflixFastMeasurementResult(
            id=("1"),
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            asn=None,
            ip=None,
            isp=None,
            city=None,
            country=None,
            urlcount=self.nft.urlcount,
            reason_terminated=None,
            errors=[
                Error(
                    key="netflix-script-response",
                    description=NETFLIX_ERRORS.get("netflix-script-response", ""),
                    traceback="Failed to pretend to establish a new connection",
                )
            ],
        )
        mock_session = mock.MagicMock()
        mock_resp = mock.MagicMock()
        mock_resp.text = '<script src="(This is the script)">'
        mock_session.get.side_effect = [
            mock_resp,
            ConnectionError("Failed to pretend to establish a new connection"),
        ]
        mock_get_session.return_value = mock_session
        assert self.nft._get_fast_result() == mock_error_result

    @mock.patch("requests.Session")
    def test_netflix_token_regex_err(self, mock_get_session):
        mock_error_result = NetflixFastMeasurementResult(
            id=("1"),
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            asn=None,
            ip=None,
            isp=None,
            city=None,
            country=None,
            urlcount=self.nft.urlcount,
            reason_terminated=None,
            errors=[
                Error(
                    key="netflix-token-regex",
                    description=NETFLIX_ERRORS.get("netflix-token-regex", ""),
                    traceback='This is an invalid script response, containing BRoken:"This is the token"',
                )
            ],
        )
        mock_session = mock.MagicMock()
        mock_resp = mock.MagicMock()
        mock_resp.text = '<script src="(This is the script)">'
        mock_script_resp = mock.MagicMock()
        mock_script_resp.text = (
            'This is an invalid script response, containing BRoken:"This is the token"'
        )
        mock_session.get.side_effect = [mock_resp, mock_script_resp]
        mock_get_session.return_value = mock_session
        assert self.nft._get_fast_result() == mock_error_result

    @mock.patch("requests.Session")
    def test_netflix_api_response_err(self, mock_get_session):
        mock_error_result = NetflixFastMeasurementResult(
            id=("1"),
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            asn=None,
            ip=None,
            isp=None,
            city=None,
            country=None,
            urlcount=self.nft.urlcount,
            reason_terminated=None,
            errors=[
                Error(
                    key="netflix-api-response",
                    description=NETFLIX_ERRORS.get("netflix-api-response", ""),
                    traceback="Failed to pretend to establish a new connection",
                )
            ],
        )
        mock_session = mock.MagicMock()
        mock_resp = mock.MagicMock()
        mock_resp.text = '<script src="(This is the script)">'
        mock_script_resp = mock.MagicMock()
        mock_script_resp.text = (
            'This is the script response, containing token:"This is the token"'
        )
        mock_session.get.side_effect = [
            mock_resp,
            mock_script_resp,
            ConnectionError("Failed to pretend to establish a new connection"),
        ]
        mock_get_session.return_value = mock_session
        assert self.nft._get_fast_result() == mock_error_result

    @mock.patch("requests.Session")
    def test_netflix_api_json_err(self, mock_get_session):
        mock_error_result = NetflixFastMeasurementResult(
            id=("1"),
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            asn=None,
            ip=None,
            isp=None,
            city=None,
            country=None,
            urlcount=self.nft.urlcount,
            reason_terminated=None,
            errors=[
                Error(
                    key="netflix-api-json",
                    description=NETFLIX_ERRORS.get("netflix-api-json", ""),
                    traceback="Json Decode screwed up :(: line 1 column 1 (char 0)",
                )
            ],
        )
        mock_session = mock.MagicMock()
        mock_resp = mock.MagicMock()
        mock_resp.text = '<script src="(This is the script)">'
        mock_script_resp = mock.MagicMock()
        mock_script_resp.text = (
            'This is the script response, containing token:"This is the token"'
        )
        mock_api_resp = mock.MagicMock()
        mock_api_resp.json.side_effect = json.decoder.JSONDecodeError(
            "Json Decode screwed up :(", "{BuSTED_JSON ::: asdf}", 0
        )
        mock_session.get.side_effect = [mock_resp, mock_script_resp, mock_api_resp]
        mock_get_session.return_value = mock_session
        assert self.nft._get_fast_result() == mock_error_result

    @mock.patch("requests.Session")
    def test_netflix_api_parse_err(self, mock_get_session):
        mock_error_result = NetflixFastMeasurementResult(
            id=("1"),
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            asn=None,
            ip=None,
            isp=None,
            city=None,
            country=None,
            urlcount=self.nft.urlcount,
            reason_terminated=None,
            errors=[
                Error(
                    key="netflix-api-parse",
                    description=NETFLIX_ERRORS.get("netflix-api-parse", ""),
                    traceback="string indices must be integers, not 'str'",
                )
            ],
        )
        # JSONDecodeError changed in 3.11
        if sys.version_info < (3, 11):
            mock_error_result = NetflixFastMeasurementResult(
                id=("1"),
                download_rate=None,
                download_rate_unit=None,
                download_size=None,
                download_size_unit=None,
                asn=None,
                ip=None,
                isp=None,
                city=None,
                country=None,
                urlcount=self.nft.urlcount,
                reason_terminated=None,
                errors=[
                    Error(
                        key="netflix-api-parse",
                        description=NETFLIX_ERRORS.get("netflix-api-parse", ""),
                        traceback="string indices must be integers",
                    )
                ],
            )
        mock_session = mock.MagicMock()
        mock_resp = mock.MagicMock()
        mock_resp.text = '<script src="(This is the script)">'
        mock_script_resp = mock.MagicMock()
        mock_script_resp.text = (
            'This is the script response, containing token:"This is the token"'
        )
        mock_api_resp = mock.MagicMock()
        mock_api_resp.json.side_effect = {"correct_values": "are not in here >:)"}
        mock_session.get.side_effect = [mock_resp, mock_script_resp, mock_api_resp]
        mock_get_session.return_value = mock_session
        assert self.nft._get_fast_result() == mock_error_result

    @mock.patch("requests.Session")
    def test_netflix_api_parse_targets_err(self, mock_get_session):
        mock_error_result = NetflixFastMeasurementResult(
            id=("1"),
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            asn=None,
            ip=None,
            isp=None,
            city=None,
            country=None,
            urlcount=self.nft.urlcount,
            reason_terminated=None,
            errors=[
                Error(
                    key="netflix-api-parse",
                    description=NETFLIX_ERRORS.get("netflix-api-parse", ""),
                    traceback="0",
                )
            ],
        )
        mock_session = mock.MagicMock()
        mock_resp = mock.MagicMock()
        mock_resp.text = '<script src="(This is the script)">'
        mock_script_resp = mock.MagicMock()
        mock_script_resp.text = (
            'This is the script response, containing token:"This is the token"'
        )
        mock_api_resp = mock.MagicMock()
        mock_api_resp.json = mock.MagicMock()
        mock_api_resp.json.side_effect = [
            {"targets": {"correct_values": "are not in here >:)"}}
        ]
        mock_session.get.side_effect = [mock_resp, mock_script_resp, mock_api_resp]
        mock_get_session.return_value = mock_session
        assert self.nft._get_fast_result() == mock_error_result

    @mock.patch("requests.Session")
    def test_netflix_connection_err(self, mock_get_session):
        mock_error_result = NetflixFastMeasurementResult(
            id=("1"),
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            asn=None,
            ip=None,
            isp=None,
            city=None,
            country=None,
            urlcount=self.nft.urlcount,
            reason_terminated=None,
            errors=[
                Error(
                    key="netflix-connection",
                    description=NETFLIX_ERRORS.get("netflix-connection", ""),
                    traceback="Failed to pretend to establish a new connection",
                )
            ],
        )
        mock_session = mock.MagicMock()
        mock_resp = mock.MagicMock()
        mock_resp.text = '<script src="(This is the script)">'
        mock_script_resp = mock.MagicMock()
        mock_script_resp.text = (
            'This is the script response, containing token:"This is the token"'
        )
        mock_api_resp = mock.MagicMock()
        mock_api_resp.json.side_effect = [
            {
                "client": {},
                "targets": [
                    {
                        "url": "https://afakeurl.1.notreal.net/speedtest",
                        "location": {
                            "city": "Foreign City One",
                            "country": "Foreign Country One",
                        },
                    }
                ],
            }
        ]
        mock_session.get.side_effect = [
            mock_resp,
            mock_script_resp,
            mock_api_resp,
            ConnectionError("Failed to pretend to establish a new connection"),
        ]
        mock_get_session.return_value = mock_session
        self.nft.thread_results = [
            {
                "index": i,
                "elapsed_time": None,
                "download_size": 0,
                "download_rate": 0,
                "url": None,
                "location": None,
            }
            for i in range(self.nft.urlcount)  # Generate thread results dict structure
        ]
        assert self.nft._get_fast_result() == mock_error_result
