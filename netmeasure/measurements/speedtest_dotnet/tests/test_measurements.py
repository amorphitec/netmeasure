import subprocess
from unittest import TestCase, mock

import speedtest

from netmeasure.measurements.speedtest_dotnet.measurements import (
    SpeedtestDotnetMeasurement,
    SPEEDTEST_ERRORS,
)
from netmeasure.measurements.speedtest_dotnet.results import (
    SpeedtestDotnetMeasurementResult,
)
from netmeasure.measurements.base.results import Error
from netmeasure.units import RatioUnit, TimeUnit, StorageUnit, NetworkUnit


class SpeedtestDotnetTestCase(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        super().setUp()
        self.id = "1"
        self.stdnm = SpeedtestDotnetMeasurement("1")
        self.sample_results_dict_valid = {
            "download": 93116804.64881887,
            "upload": 19256654.06593738,
            "ping": 17.054,
            "server": {
                "url": "http://fake.site:8080/speedtest/upload.php",
                "lat": "-33.8600",
                "lon": "151.2111",
                "name": "HonestyVille",
                "country": "Australia",
                "cc": "AU",
                "sponsor": "'Yes' HonestyBox",
                "id": "1267",
                "url2": "http://s1.fake.site:8080/speedtest/upload.php",
                "host": "fake.site:8080",
                "d": 53.70823411720704,
                "latency": 17.054,
            },
            "timestamp": "2020-03-11T07:09:52.890803Z",
            "bytes_sent": 25591808,
            "bytes_received": 116746522,
            "share": "http://www.faketest.net/result/9117363621.png",
            "client": {
                "ip": "101.166.54.134",
                "lat": "-33.4102",
                "lon": "151.4225",
                "isp": "HonestyBox Internet",
                "isprating": "3.7",
                "rating": "0",
                "ispdlavg": "0",
                "ispulavg": "0",
                "loggedin": "0",
                "country": "AU",
            },
        }
        self.sample_result_valid = SpeedtestDotnetMeasurementResult(
            id=self.id,
            download_rate=93116804.64881887,
            download_rate_unit=NetworkUnit("bit/s"),
            upload_rate=19256654.06593738,
            upload_rate_unit=NetworkUnit("bit/s"),
            data_received=116746522,
            data_received_unit=StorageUnit("B"),
            latency=17.054,
            server_name="HonestyVille",
            server_id="1267",
            server_sponsor="'Yes' HonestyBox",
            server_host="fake.site:8080",
            errors=[],
        )
        self.sample_result_configretrieval = SpeedtestDotnetMeasurementResult(
            id=self.id,
            download_rate=None,
            download_rate_unit=None,
            upload_rate=None,
            upload_rate_unit=None,
            data_received=None,
            data_received_unit=None,
            latency=None,
            server_name=None,
            server_id=None,
            server_sponsor=None,
            server_host=None,
            errors=[
                Error(
                    key="speedtest-config",
                    description=SPEEDTEST_ERRORS.get("speedtest-config", ""),
                    traceback="<urlopen error [Errno -3] Temporary failure in name resolution>",
                )
            ],
        )
        self.sample_result_bestserver = SpeedtestDotnetMeasurementResult(
            id=self.id,
            download_rate=None,
            download_rate_unit=None,
            upload_rate=None,
            upload_rate_unit=None,
            data_received=None,
            data_received_unit=None,
            latency=None,
            server_name=None,
            server_id=None,
            server_sponsor=None,
            server_host=None,
            errors=[
                Error(
                    key="speedtest-best-server",
                    description=SPEEDTEST_ERRORS.get("speedtest-best-server", ""),
                    traceback="Unable to connect to servers to test latency.",
                )
            ],
        )
        self.sample_result_share = SpeedtestDotnetMeasurementResult(
            id=self.id,
            download_rate=None,
            download_rate_unit=None,
            upload_rate=None,
            upload_rate_unit=None,
            data_received=None,
            data_received_unit=None,
            latency=None,
            server_name=None,
            server_id=None,
            server_sponsor=None,
            server_host=None,
            errors=[
                Error(
                    key="speedtest-share",
                    description=SPEEDTEST_ERRORS.get("speedtest-share", ""),
                    traceback="<urlopen error [Errno -3] Temporary failure in name resolution>",
                )
            ],
        )

    @mock.patch("speedtest.Speedtest")
    def test_speedtest(self, mock_speedtest_constructor):
        run_mock = mock.Mock()
        results_mock = mock.Mock()
        results_mock.share = mock.Mock(return_value=None)
        results_mock.dict = mock.Mock(return_value=self.sample_results_dict_valid)
        run_mock.results = results_mock

        mock_speedtest_constructor.return_value = run_mock
        result = self.stdnm.measure()
        self.assertEqual(result, self.sample_result_valid)

    @mock.patch("speedtest.Speedtest")
    def test_speedtest_config_failure(self, mock_speedtest_constructor):
        mock_speedtest_constructor.side_effect = speedtest.ConfigRetrievalError(
            "<urlopen error [Errno -3] Temporary failure in name resolution>"
        )
        result = self.stdnm.measure()
        self.assertEqual(result, self.sample_result_configretrieval)

    @mock.patch("speedtest.Speedtest")
    def test_speedtest_get_best_server_failure(self, mock_speedtest_constructor):
        run_mock = mock.Mock()
        run_mock.get_best_server.side_effect = speedtest.SpeedtestBestServerFailure(
            "Unable to connect to servers to test latency."
        )
        mock_speedtest_constructor.return_value = run_mock
        result = self.stdnm.measure()
        self.assertEqual(result, self.sample_result_bestserver)

    @mock.patch("speedtest.Speedtest")
    def test_speedtest_share_results_failure(self, mock_speedtest_constructor):
        run_mock = mock.Mock()
        results_mock = mock.Mock()
        results_mock.share = mock.Mock(
            side_effect=speedtest.ShareResultsConnectFailure(
                "<urlopen error [Errno -3] Temporary failure in name resolution>"
            )
        )
        run_mock.results = results_mock
        mock_speedtest_constructor.return_value = run_mock
        result = self.stdnm.measure(share=True)
        self.assertEqual(result, self.sample_result_share)
