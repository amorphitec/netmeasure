# -*- coding: utf-8 -*-
from unittest import TestCase, mock
from unittest.mock import call

import six
import subprocess

from netmeasure.measurements.latency.measurements import LatencyMeasurement
from netmeasure.measurements.base.results import Error
from netmeasure.measurements.webpage_download.measurements import (
    WebpageDownloadMeasurement,
)
from netmeasure.measurements.webpage_download.measurements import WEB_ERRORS

from netmeasure.measurements.webpage_download.results import (
    WebpageDownloadMeasurementResult,
)
from netmeasure.measurements.latency.results import LatencyMeasurementResult

from netmeasure.units import NetworkUnit, StorageUnit, TimeUnit, RatioUnit


class WebpageDownloadMeasurementResultsTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.wpm = WebpageDownloadMeasurement("test", "http://validfakehost.com/test")
        self.simple_webpage_output = WebpageDownloadMeasurementResult(
            id="test",
            url="http://validfakehost.com/test",
            download_rate=100 / 1.00 * 8,
            download_rate_unit=NetworkUnit("bit/s"),
            download_size=100,
            download_size_unit=StorageUnit("B"),
            asset_count=123,
            failed_asset_downloads=0,
            elapsed_time=1.00,
            elapsed_time_unit=TimeUnit("s"),
            errors=[],
        )
        self.simple_asset_download_metrics = {
            "asset_download_size": 90,
            "failed_asset_downloads": 0,
            "completion_time": 2.00,
        }
        self.get_error_result = WebpageDownloadMeasurementResult(
            id="test",
            url="http://validfakehost.com/test",
            download_rate_unit=None,
            download_rate=None,
            download_size=None,
            download_size_unit=None,
            asset_count=None,
            failed_asset_downloads=None,
            elapsed_time=None,
            elapsed_time_unit=None,
            errors=[
                Error(
                    key="web-get",
                    description=WEB_ERRORS.get("web-get", ""),
                    traceback="[Errno -2] Name or service not known",
                )
            ],
        )

    @mock.patch(
        "netmeasure.measurements.webpage_download.measurements.WebpageDownloadMeasurement._get_webpage_result"
    )
    def test_measure(self, mock_get_webpage):
        mock_get_webpage.return_value = self.simple_webpage_output
        self.assertEqual(self.wpm.measure(), self.simple_webpage_output)

    @mock.patch(
        "netmeasure.measurements.webpage_download.measurements.WebpageDownloadMeasurement._download_assets"
    )
    @mock.patch(
        "netmeasure.measurements.webpage_download.measurements.WebpageDownloadMeasurement._parse_html"
    )
    @mock.patch("requests.Session")
    @mock.patch("time.time")
    def test_get_requests_measurement(
        self, mock_time, mock_get_session, mock_parse_html, mock_download_assets
    ):
        mock_time.return_value = 1.00
        mock_session = mock.MagicMock()
        mock_resp = mock.MagicMock()
        # Total 'downloaded' size is 100 bytes
        mock_resp.text = "Ten chars_"
        mock_session.get.side_effect = [mock_resp]
        mock_parse_html.return_value = [
            "URL number {x}".format(x=i + 1) for i in range(123)
        ]
        mock_download_assets.return_value = self.simple_asset_download_metrics
        mock_get_session.return_value = mock_session
        self.assertEqual(
            self.wpm._get_webpage_result(
                "http://validfakehost.com/test", "validfakehost.com", "https"
            ),
            self.simple_webpage_output,
        )

    @mock.patch(
        "netmeasure.measurements.webpage_download.measurements.WebpageDownloadMeasurement._download_assets"
    )
    @mock.patch(
        "netmeasure.measurements.webpage_download.measurements.WebpageDownloadMeasurement._parse_html"
    )
    @mock.patch("requests.Session")
    @mock.patch("time.time")
    def test_get_requests_error(
        self, mock_time, mock_get_session, mock_parse_html, mock_download_assets
    ):
        mock_time.return_value = 1.00
        mock_session = mock.MagicMock()
        mock_session.get.side_effect = [
            ConnectionError("[Errno -2] Name or service not known")
        ]
        mock_get_session.return_value = mock_session
        self.assertEqual(
            self.wpm._get_webpage_result(
                "http://validfakehost.com/test", "validfakehost.com", "https"
            ),
            self.get_error_result,
        )


class WebpageHTMLParseTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.wpm = WebpageDownloadMeasurement("test", "http://validfakehost.com/test")
        self.img_html = (
            '<img alt="HBOX" id="logo" src="/logo/src/name.png"/>\n'
            '<img alt="HBOX" id="another" src="/another/src/name.png"/>\n'
            '<img alt="HBOX" id="ayylmao" src="/ayylmao/src/name.png"/>\n'
            '<img alt="HBOX" id="no source"/>\n'
        )
        self.img_urls = [
            "/logo/src/name.png",
            "/another/src/name.png",
            "/ayylmao/src/name.png",
        ]
        self.script_html = (
            '<script src="/script_one/src/name.js"/>\n'
            '<script src="/script_two/src/name.js"/>\n'
            '<script src="/script_three/src/name.js"/>\n'
            "<script/>\n"
        )
        self.script_urls = [
            "/script_one/src/name.js",
            "/script_two/src/name.js",
            "/script_three/src/name.js",
        ]
        self.link_html = (
            '<link href="http://validfakehost.com/test" rel="manifest"/>\n'
            '<link href="http://externalfakehost.com/one" rel="modulepreload"/>\n'
            '<link href="http://externalfakehost.com/two" rel="preload"/>\n'
            '<link href="http://externalfakehost.com/three" rel="prerender"/>\n'
            '<link href="http://externalfakehost.com/four.css" rel="stylesheet"/>\n'
            '<link href="http://externalfakehost.com/five.png" rel="apple-touch-icon"/>\n'
            '<link href="http://externalfakehost.com/six.ico" rel="icon"/>\n'
            '<link href="http://externalfakehost.com/seven.ico" rel="shortcut icon"/>\n'
            '<link href="http://externalfakehost.com/eight.txt" rel="dont care"/>\n'
            '<link href="http://externalfakehost.com/no_rel.txt"/>\n'
            '<link rel="icon"/>\n'
        )
        self.link_urls = [
            "http://validfakehost.com/test",
            "http://externalfakehost.com/one",
            "http://externalfakehost.com/two",
            "http://externalfakehost.com/three",
            "http://externalfakehost.com/four.css",
            "http://externalfakehost.com/five.png",
            "http://externalfakehost.com/six.ico",
            "http://externalfakehost.com/seven.ico",
        ]

    def test_parse_img(self):
        self.assertEqual(self.wpm._parse_html(self.img_html), self.img_urls)

    def test_parse_script(self):
        self.assertEqual(self.wpm._parse_html(self.script_html), self.script_urls)

    def test_parse_links(self):
        self.assertEqual(self.wpm._parse_html(self.link_html), self.link_urls)


class WebpageAssetDownloadTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.wpm = WebpageDownloadMeasurement("test", "http://validfakehost.com/test")
        self.all_url_types = [
            "https://validfakehost.com/an_image.jpg",
            "/resources/client/a_stylesheet.css",
            "//res.validfakehost.com/fonts/a_font.woff2",
        ]
        self.all_success_urls_transformed = [
            call(
                "https://validfakehost.com/an_image.jpg",
                timeout=self.wpm.download_timeout,
            ),
            call(
                "https://validfakehost.com/resources/client/a_stylesheet.css",
                timeout=self.wpm.download_timeout,
            ),
            call(
                "https://res.validfakehost.com/fonts/a_font.woff2",
                timeout=self.wpm.download_timeout,
            ),
        ]
        self.all_success_dict = {
            "asset_download_size": 3,
            "failed_asset_downloads": 0,
            "completion_time": 1.23,
        }
        self.one_failure_dict = {
            "asset_download_size": 2,
            "failed_asset_downloads": 1,
            "completion_time": 1.23,
        }
        self.all_failure_dict = {
            "asset_download_size": 0,
            "failed_asset_downloads": 3,
            "completion_time": 1.23,
        }

    @mock.patch("time.time")
    def test_all_success_dict(self, mock_time):
        mock_time.return_value = 1.23
        mock_session = mock.MagicMock()
        responses = []
        for i in range(3):
            response = mock.MagicMock()
            response.text = str("i")
            response.status_code = 200
            responses.append(response)
        mock_session.get.side_effect = responses
        self.assertEqual(
            self.wpm._download_assets(
                mock_session, self.all_url_types, "validfakehost.com", "https"
            ),
            self.all_success_dict,
        )

    def test_all_success_urls(self):
        mock_session = mock.MagicMock()
        responses = []
        for i in range(3):
            response = mock.MagicMock()
            response.text = str("i")
            response.status_code = 200
            responses.append(response)
        mock_session.get.side_effect = responses
        self.wpm._download_assets(
            mock_session, self.all_url_types, "validfakehost.com", "https"
        )
        mock_session.get.assert_has_calls(self.all_success_urls_transformed)

    @mock.patch("time.time")
    def test_single_failure_code(self, mock_time):
        mock_time.return_value = 1.23
        mock_session = mock.MagicMock()
        responses = []
        for i in range(2):
            response = mock.MagicMock()
            response.text = str("i")
            response.status_code = 200
            responses.append(response)
        fail_response = mock.MagicMock()
        fail_response.text = "0"
        fail_response.status_code = 404
        responses.append(fail_response)
        mock_session.get.side_effect = responses
        self.assertEqual(
            self.wpm._download_assets(
                mock_session, self.all_url_types, "validfakehost.com", "https"
            ),
            self.one_failure_dict,
        )

    @mock.patch("time.time")
    def test_single_failure_error(self, mock_time):
        mock_time.return_value = 1.23
        mock_session = mock.MagicMock()
        responses = []
        for i in range(2):
            response = mock.MagicMock()
            response.text = str("i")
            response.status_code = 200
            responses.append(response)
        responses.append(ConnectionError)
        mock_session.get.side_effect = responses
        self.assertEqual(
            self.wpm._download_assets(
                mock_session, self.all_url_types, "validfakehost.com", "https"
            ),
            self.one_failure_dict,
        )

    @mock.patch("time.time")
    def test_all_failure(self, mock_time):
        mock_time.return_value = 1.23
        mock_session = mock.MagicMock()
        responses = []
        for i in range(2):
            response = mock.MagicMock()
            response.text = str("i")
            response.status_code = 404
            responses.append(response)
        responses.append(ConnectionError)
        mock_session.get.side_effect = responses
        self.assertEqual(
            self.wpm._download_assets(
                mock_session, self.all_url_types, "validfakehost.com", "https"
            ),
            self.all_failure_dict,
        )
