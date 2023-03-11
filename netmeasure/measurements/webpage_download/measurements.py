import time
from six.moves.urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from netmeasure.measurements.base.measurements import BaseMeasurement
from netmeasure.measurements.base.results import Error
from netmeasure.units import RatioUnit, TimeUnit, StorageUnit, NetworkUnit
from netmeasure.measurements.webpage_download.results import (
    WebpageDownloadMeasurementResult,
)
from netmeasure.measurements.latency.measurements import LatencyMeasurement


WEB_ERRORS = {
    "web-get": "Failed to complete the initial connection",
    "web-parse": "Failed to parse assets from HTML",
    "web-parse-rel": "Failed to determine 'rel' attribute of link",
    "web-assets": "Failed to download secondary assets",
    "web-timeout": "Initial page download timed out",
}
VALID_LINK_EXTENSTIONS = [".css", ".ico", ".png", ".woff2", ""]
VALID_LINK_REL_ATTRIBUTES = [
    "manifest",
    "modulepreload",
    "preload",
    "prerender",
    "stylesheet",
    "apple-touch-icon",
    "icon",
    "shortcut icon",
]


class WebpageDownloadMeasurement(BaseMeasurement):
    def __init__(self, id, url, count=4, download_timeout=180):
        self.id = id
        self.url = url
        self.count = count
        self.download_timeout = download_timeout

    def measure(self):
        host = urlparse(self.url).netloc
        protocol = urlparse(self.url).scheme
        return self._get_webpage_result(self.url, host, protocol)

    def _get_webpage_result(self, url, host, protocol):
        s = requests.Session()
        headers = {
            "dnt": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        }

        start_time = time.time()
        try:
            r = s.get(url, headers=headers, timeout=self.download_timeout)
        except (ConnectionError, requests.ConnectionError) as e:
            return self._get_webpage_error("web-get", traceback=str(e))
        except requests.exceptions.ReadTimeout as e:
            return self._get_webpage_error("web-timeout", traceback=str(e))
        try:
            to_download = self._parse_html(r.text)
        except TypeError as e:
            return self._get_webpage_error("web-parse-rel", traceback=str(e))
        try:
            asset_download_metrics = self._download_assets(
                s, to_download, host, protocol
            )
        except TypeError as e:
            return self._get_webpage_error("web-assets", traceback=str(e))

        primary_download_size = len(r.text)
        asset_download_size = asset_download_metrics["asset_download_size"]
        elapsed_time = asset_download_metrics["completion_time"] - start_time
        download_rate = (primary_download_size + asset_download_size) * 8 / elapsed_time
        failed_asset_downloads = asset_download_metrics["failed_asset_downloads"]

        return WebpageDownloadMeasurementResult(
            id=self.id,
            url=url,
            download_rate=download_rate,
            download_rate_unit=NetworkUnit("bit/s"),
            download_size=primary_download_size + asset_download_size,
            download_size_unit=StorageUnit("B"),
            asset_count=len(to_download),
            failed_asset_downloads=failed_asset_downloads,
            elapsed_time=elapsed_time,
            elapsed_time_unit=TimeUnit("s"),
            errors=[],
        )

    def _parse_html(self, content):
        soup = BeautifulSoup(content, "html.parser")
        imgs = soup.find_all("img")
        links = soup.find_all("link")
        scripts = soup.find_all("script")
        to_download = []
        for img in imgs:
            if img.has_attr("src"):
                to_download.append(img["src"])
        for script in scripts:
            if script.has_attr("src"):
                to_download.append(script["src"])
        for link in links:
            if link.has_attr("rel") & link.has_attr("href"):
                # Join in the case where `rel` is more than one word
                rel = " ".join(link["rel"])
                if rel in VALID_LINK_REL_ATTRIBUTES:
                    to_download.append(link["href"])

        return to_download

    def _download_assets(self, session, to_download, host, protocol):
        # Store the amount of bytes downloaded
        asset_download_sizes = []
        failed_asset_downloads = 0
        for asset in to_download:
            try:
                # Identify data URLs (already downloaded inline, counted in main download size)
                if "data:" in asset:
                    continue

                # Check if path w/o preceeding slashes is a valid URL
                if asset.startswith("//"):
                    download_url = protocol + ":" + asset
                # Check if path is a relative path
                elif asset.startswith("/"):
                    download_url = protocol + "://" + host + asset
                # ...or simply a normal file link
                else:
                    download_url = asset

                a = session.get(download_url, timeout=self.download_timeout)
                if a.status_code >= 400:
                    raise ConnectionError
                asset_download_sizes.append(len(a.text))
            except ConnectionError:
                failed_asset_downloads = failed_asset_downloads + 1
            except requests.exceptions.MissingSchema:
                failed_asset_downloads = failed_asset_downloads + 1
            except requests.exceptions.ReadTimeout:
                failed_asset_downloads = failed_asset_downloads + 1

        return {
            "asset_download_size": sum(asset_download_sizes),
            "failed_asset_downloads": failed_asset_downloads,
            "completion_time": time.time(),
        }

    def _get_webpage_error(self, key, traceback):
        return WebpageDownloadMeasurementResult(
            id=self.id,
            url=self.url,
            download_rate_unit=None,
            download_rate=None,
            download_size=None,
            download_size_unit=None,
            asset_count=None,
            failed_asset_downloads=None,
            elapsed_time=None,
            elapsed_time_unit=None,
            errors=[
                Error(key=key, description=WEB_ERRORS.get(key, ""), traceback=traceback)
            ],
        )
