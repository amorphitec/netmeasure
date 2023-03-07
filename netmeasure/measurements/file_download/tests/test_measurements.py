# -*- coding: utf-8 -*-
from unittest import TestCase, mock
import six
import subprocess

from netmeasure.measurements.latency.measurements import LatencyMeasurement
from netmeasure.measurements.base.results import Error
from netmeasure.measurements.file_download.measurements import WGET_OUTPUT_REGEX
from netmeasure.measurements.file_download.measurements import FileDownloadMeasurement
from netmeasure.measurements.file_download.measurements import WGET_ERRORS
from netmeasure.measurements.file_download.results import FileDownloadMeasurementResult
from netmeasure.measurements.latency.results import LatencyMeasurementResult

from netmeasure.units import NetworkUnit, StorageUnit

# NOTE: To match what subprocess calls output, wget output strings
#       should end with "\n\n" and latency output strings should end with "\n"


def test_wget_output_regex_accepts_anticipated_format():
    anticipated_format = six.ensure_str(
        "2019-08-07 09:12:08 (16.7 MB/s) - '/dev/null’ saved [11376]"
    )
    results = WGET_OUTPUT_REGEX.search(anticipated_format).groupdict()
    assert results == {
        "download_rate": "16.7",
        "download_size": "11376",
        "download_unit": "MB/s",
    }


class FileDownloadMeasurementCreationTestCase(TestCase):
    def test_invalid_hosts(self, *args):
        self.assertRaises(
            ValueError, FileDownloadMeasurement, "test", ["invalid..host"]
        )

    def test_invalid_count(self, *args):
        self.assertRaises(
            TypeError,
            FileDownloadMeasurement,
            "test",
            ["http://validfakeurl.com"],
            count="invalid-count",
        )

    def test_invalid_negative_count(self, *args):
        self.assertRaises(
            ValueError,
            FileDownloadMeasurement,
            "test",
            ["http://validfakeurl.com"],
            count=-2,
        )


class FileDownloadMeasurementWgetTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.measurement = FileDownloadMeasurement(
            "test", ["https://validfakehost.com/test"]
        )
        self.valid_wget_kibit_sec = FileDownloadMeasurementResult(
            id="test",
            url="http://validfakehost.com/test",
            download_rate_unit=NetworkUnit("Kibit/s"),
            download_rate=133.6,
            download_size=11376,
            download_size_unit=StorageUnit.bit,
            errors=[],
        )
        self.valid_wget_mibit_sec = FileDownloadMeasurementResult(
            id="test",
            url="http://validfakehost.com/test",
            download_rate_unit=NetworkUnit("Mibit/s"),
            download_rate=133.6,
            download_size=11376,
            download_size_unit=StorageUnit.bit,
            errors=[],
        )
        self.invalid_wget_mibit_sec = FileDownloadMeasurementResult(
            id="test",
            url="http://validfakehost.com/test",
            download_rate_unit=None,
            download_rate=None,
            download_size=None,
            download_size_unit=None,
            errors=[
                Error(
                    key="wget-err",
                    description=WGET_ERRORS.get("wget-err", ""),
                    traceback="\n2019-08-07 09:12:08 (16.7 MB/s) - '/dev/null’ saved [11376]\n\n",
                )
            ],
        )
        self.invalid_wget_download_unit = FileDownloadMeasurementResult(
            id="test",
            url="http://validfakehost.com/test",
            download_rate_unit=None,
            download_rate=None,
            download_size=None,
            download_size_unit=None,
            errors=[
                Error(
                    key="wget-download-unit",
                    description=WGET_ERRORS.get("wget-download-unit", ""),
                    traceback="\n2019-08-07 09:12:08 (16.7 TB/s) - '/dev/null’ saved [11376]\n\n",
                )
            ],
        )
        self.invalid_regex = FileDownloadMeasurementResult(
            id="test",
            url="http://validfakehost.com/test",
            download_rate_unit=None,
            download_rate=None,
            download_size=None,
            download_size_unit=None,
            errors=[
                Error(
                    key="wget-regex",
                    description=WGET_ERRORS.get("wget-regex", ""),
                    traceback="\n2019-08-07 09:12:08 [BAD REGEX]\n\n",
                )
            ],
        )

    @mock.patch("subprocess.run")
    def test_valid_wget_kibit_sec(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="b''",
            stderr="\n2019-08-07 09:12:08 (16.7 KB/s) - '/dev/null’ saved [11376]\n\n",
        )
        self.assertEqual(
            self.valid_wget_kibit_sec,
            self.measurement._get_wget_results(
                "http://validfakehost.com/test", self.measurement.download_timeout
            ),
        )

    @mock.patch("subprocess.run")
    def test_valid_wget_mibit_sec(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="b''",
            stderr="\n2019-08-07 09:12:08 (16.7 MB/s) - '/dev/null’ saved [11376]\n\n",
        )
        self.assertEqual(
            self.valid_wget_mibit_sec,
            self.measurement._get_wget_results(
                "http://validfakehost.com/test", self.measurement.download_timeout
            ),
        )

    @mock.patch("subprocess.run")
    def test_invalid_wget(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="b''",
            stderr="\n2019-08-07 09:12:08 (16.7 MB/s) - '/dev/null’ saved [11376]\n\n",
        )
        self.assertEqual(
            self.invalid_wget_mibit_sec,
            self.measurement._get_wget_results(
                "http://validfakehost.com/test", self.measurement.download_timeout
            ),
        )

    @mock.patch("subprocess.run")
    def test_invalid_wget_download_unit(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="b''",
            stderr="\n2019-08-07 09:12:08 (16.7 TB/s) - '/dev/null’ saved [11376]\n\n",
        )
        self.assertEqual(
            self.invalid_wget_download_unit,
            self.measurement._get_wget_results(
                "http://validfakehost.com/test", self.measurement.download_timeout
            ),
        )

    @mock.patch("subprocess.run")
    def test_wget_invalid_regex(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="b''",
            stderr="\n2019-08-07 09:12:08 [BAD REGEX]\n\n",
        )
        self.assertEqual(
            self.invalid_regex,
            self.measurement._get_wget_results(
                "http://validfakehost.com/test", self.measurement.download_timeout
            ),
        )


class FileDownloadMeasurementClosestServerTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.example_urls = [
            "http://n1-validfakehost.com",
            "http://n2-validfakehost.com",
            "http://n3-validfakehost.com",
        ]
        self.measurement = FileDownloadMeasurement("test", self.example_urls)
        print("asdf")

    @mock.patch.object(LatencyMeasurement, "measure")
    def test_sort_least_latent_url(self, mock_latency_results):
        results = [
            (
                LatencyMeasurementResult(
                    id="test",
                    host="n1-validfakehost.com",
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
                    id="test",
                    host="n2-validfakehost.com",
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
                    id="test",
                    host="n3-validfakehost.com",
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
        mock_latency_results.side_effect = results
        self.assertEqual(
            self.measurement._find_least_latent_url(self.example_urls),
            [
                (self.example_urls[1], results[1][0]),
                (self.example_urls[2], results[2][0]),
                (self.example_urls[0], results[0][0]),
            ],
        )

    @mock.patch.object(LatencyMeasurement, "measure")
    def test_sort_one_url(self, mock_latency_results):
        results = [
            (
                LatencyMeasurementResult(
                    id="test",
                    host="n2-validfakehost.com",
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
            )
        ]
        mock_latency_results.side_effect = results
        self.assertEqual(
            self.measurement._find_least_latent_url([self.example_urls[1]]),
            [(self.example_urls[1], results[0][0])],
        )
