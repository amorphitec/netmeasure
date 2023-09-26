import re

import validators
import subprocess
from six.moves.urllib.parse import urlparse
from validators import ValidationFailure

from netmeasure.measurements.base.measurements import BaseMeasurement
from netmeasure.measurements.file_download.results import FileDownloadMeasurementResult
from netmeasure.measurements.latency.measurements import LatencyMeasurement
from netmeasure.measurements.base.results import Error
from netmeasure.units import NetworkUnit, StorageUnit

WGET_OUTPUT_REGEX = re.compile(
    r"\((?P<download_rate>[\d.]*)\s(?P<download_unit>.*)\).*\[(?P<download_size>\d*)[\]/]"
)

WGET_ERRORS = {
    "wget-err": "wget had an unknown error.",
    "wget-split": "wget attempted to split the result but it was in an unanticipated format.",
    "wget-regex": "wget attempted get the known regex format and failed.",
    "wget-download-unit": "wget could not process the download unit.",
    "wget-download-rate": "wget could not process the download rate.",
    "wget-download-size": "wget could not process the download size.",
    "wget-no-server": "No closest server could be resolved.",
    "wget-timeout": "Measurement request timed out.",
}

WGET_DOWNLOAD_RATE_UNIT_MAP = {
    "KB/s": NetworkUnit("Kibit/s"),
    "MB/s": NetworkUnit("Mibit/s"),
}


class FileDownloadMeasurement(BaseMeasurement):
    """A measurement designed to test download speed."""

    def __init__(self, id, urls, count=4, download_timeout=180):
        """Initialisation of a download speed measurement.

        :param id: A unique identifier for the measurement.
        :param urls: A list of URLs used to perform the download speed
        measurement.
        :param count: A positive integer describing the number of
        pings to perform. Defaults to 4.
        :param download_timeout: An integer describing the number of
        seconds for the test to last. 0 means no timeout.
        """
        super(FileDownloadMeasurement, self).__init__(id=id)
        if len(urls) < 1:
            raise ValueError("At least one url must be provided.")
        for url in urls:
            validated_url = validators.url(url)
            if isinstance(validated_url, ValidationFailure):
                raise ValueError("`{url}` is not a valid url".format(url=url))

        if count < 0:
            raise ValueError(
                "A value of {count} was provided for the number of pings. This must be a positive "
                "integer or `0` to turn off the ping.".format(count=count)
            )

        if download_timeout < 0:
            raise ValueError(
                "A value of {count} was provided for the timeout. This must be a positive "
                "integer or `0` to turn off the timeout.".format(count=count)
            )

        self.urls = urls
        self.count = count
        self.download_timeout = download_timeout

    def measure(self):
        """Perform the measurement."""
        initial_latency_results = self._find_least_latent_url(self.urls)
        least_latent_url = initial_latency_results[0][0]
        results = [self._get_wget_results(least_latent_url, self.download_timeout)]
        if self.count > 0:
            host = urlparse(least_latent_url).netloc
            latency_measurement = LatencyMeasurement(self.id, host, count=self.count)
            results.append(latency_measurement.measure()[0])

        results.extend([res for _, res in initial_latency_results])
        return results

    def _find_least_latent_url(self, urls):
        """
        Performs a latency test for each specified endpoint
        Returns a sorted list of LatencyResults, sorted by average latency and None
        """
        initial_latency_results = []
        for url in urls:
            host = urlparse(url).netloc
            latency_measurement = LatencyMeasurement(self.id, host, count=2)
            initial_latency_results.append((url, latency_measurement.measure()[0]))
        return sorted(
            initial_latency_results,
            key=lambda x: (x[1].average_latency is None, x[1].average_latency),
        )

    def _get_wget_results(self, url, download_timeout):
        """Perform the download measurement."""
        if url is None:
            return self._get_wget_error("wget-no-server", url, traceback=None)

        if download_timeout == 0:
            download_timeout = None
        try:
            wget_out = subprocess.run(
                ["wget", "--tries=2", "-O", "/dev/null", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=download_timeout,
                universal_newlines=True,
            )
        except subprocess.TimeoutExpired:
            return self._get_wget_error("wget-timeout", url, traceback=None)

        if wget_out.returncode != 0:
            return self._get_wget_error("wget-err", url, traceback=wget_out.stderr)
        try:
            wget_data = wget_out.stderr.split("\n")[-3]
        except IndexError:
            return self._get_wget_error("wget-split", url, traceback=wget_out.stderr)
        matches = WGET_OUTPUT_REGEX.search(wget_data)

        try:
            match_data = matches.groupdict()
        except AttributeError:
            return self._get_wget_error("wget-regex", url, traceback=wget_out.stderr)

        if len(match_data.keys()) != 3:
            return self._get_wget_error("wget-regex", url, traceback=wget_out.stderr)

        try:
            download_rate_unit = WGET_DOWNLOAD_RATE_UNIT_MAP[
                match_data.get("download_unit")
            ]
        except KeyError:
            return self._get_wget_error(
                "wget-download-unit", url, traceback=wget_out.stderr
            )

        try:
            # NOTE: wget returns download rate in [K|M]B/s. Convert to [K|M]ibit/s.
            download_rate = float(match_data.get("download_rate")) * 8
        except (TypeError, ValueError):
            return self._get_wget_error(
                "wget-download-rate", url, traceback=wget_out.stderr
            )

        try:
            download_size = float(match_data.get("download_size"))
        except (TypeError, ValueError):
            return self._get_wget_error(
                "wget-download-size", url, traceback=wget_out.stderr
            )
        return FileDownloadMeasurementResult(
            id=self.id,
            url=url,
            download_rate_unit=download_rate_unit,
            download_rate=download_rate,
            download_size=download_size,
            download_size_unit=StorageUnit.byte,
            errors=[],
        )

    def _get_wget_error(self, key, url, traceback):
        return FileDownloadMeasurementResult(
            id=self.id,
            url=url,
            download_rate_unit=None,
            download_rate=None,
            download_size=None,
            download_size_unit=None,
            errors=[
                Error(
                    key=key, description=WGET_ERRORS.get(key, ""), traceback=traceback
                )
            ],
        )
