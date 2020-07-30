import socket
import urllib

import youtube_dl
import validators
from validators import ValidationFailure

from measurement.measurements import BaseMeasurement
from measurement.results import Error
from measurement.units import RatioUnit, TimeUnit, StorageUnit, NetworkUnit
from measurement.plugins.youtube.results import YouTubeMeasurementResult

YOUTUBE_ERRORS = {
    "youtube-download": "Download utility could not download file",
    "youtube-url": "Could not recognise URL",
}


class YouTubeMeasurement(BaseMeasurement):
    def __init__(self, id, url, path):
        super(YouTubeMeasurement, self).__init__(id=id)
        validated_url = validators.url(url)
        if isinstance(validated_url, ValidationFailure):
            raise ValueError("`{url}` is not a valid url".format(url=url))
        self.id = id
        self.url = url
        self.progress_dicts = []

    def measure(self):
        return self._get_youtube_result(self.url)

    def _get_youtube_result(self, url):
        params = {
            "verbose": True,
            "quiet": True,
            "progress_hooks": [self._store_progress_dicts_hook],
        }
        ydl = youtube_dl.YoutubeDL(params=params)
        try:
            youtube_out = ydl.extract_info(url)
        except youtube_dl.utils.DownloadError as e:
            return self._get_youtube_error("youtube-download", traceback=str(e))

        try:
            self._check_error_string(youtube_out)
        except urllib.error.URLError as e:
            return self._get_youtube_error("youtube-url", traceback=str(e))

        # Extract size and duration from final progress step
        download_size = self.progress_dicts[-1]["total_bytes"]
        elapsed_time = self.progress_dicts[-1]["elapsed"]

        # Speed is only reported in non-final steps
        download_rate = self.progress_dicts[-2]["speed"] * 8

        return YouTubeMeasurementResult(
            id=self.id,
            url=self.url,
            download_rate=download_rate,
            download_rate_unit=NetworkUnit("bit/s"),
            download_size=download_size,
            download_size_unit=StorageUnit("B"),
            elapsed_time=elapsed_time,
            elapsed_time_unit=TimeUnit("s"),
            errors=[],
        )

    def _check_error_string(self, youtube_out):
        print("Output: \n", youtube_out, "\n")

    def _store_progress_dicts_hook(self, s):
        """
        Saves the results of the download progress to a list for later parsing.
        This function is called at every progress step in the download utility
        """
        self.progress_dicts.append(s)

    def _get_youtube_error(self, key, traceback):
        return YouTubeMeasurementResult(
            id=self.id,
            url=self.url,
            download_rate_unit=None,
            download_rate=None,
            download_size=None,
            download_size_unit=None,
            elapsed_time=None,
            elapsed_time_unit=None,
            errors=[
                Error(
                    key=key,
                    description=YOUTUBE_ERRORS.get(key, ""),
                    traceback=traceback,
                )
            ],
        )
