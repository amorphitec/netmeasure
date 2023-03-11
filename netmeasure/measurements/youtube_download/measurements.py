import socket
import urllib
import time
import tempfile
import os
import shutil

import yt_dlp
import validators
from validators import ValidationFailure

from netmeasure.measurements.base.measurements import BaseMeasurement
from netmeasure.measurements.base.results import Error
from netmeasure.units import RatioUnit, TimeUnit, StorageUnit, NetworkUnit
from netmeasure.measurements.youtube_download.results import (
    YoutubeDownloadMeasurementResult,
)

YOUTUBE_ERRORS = {
    "youtube-download": "Download utility could not download file",
    "youtube-extractor": "Unable to extract info from youtube_download",
    "youtube-url": "Could not recognise URL",
    "youtube-attribute": "Could not parse attributes from progress dict",
    "youtube-progress_length": "Recorded progress dicts were too short",
    "youtube-file": "Could not remove file!!",
    "youtube-no_directory": "Could not find directory!!",
    "youtube-directory_nonempty": "Could not remove directory, non-empty!",
}


class YoutubeDownloadMeasurement(BaseMeasurement):
    def __init__(self, id, url):
        super(YoutubeDownloadMeasurement, self).__init__(id=id)
        validated_url = validators.url(url)
        if isinstance(validated_url, ValidationFailure):
            raise ValueError("`{url}` is not a valid url".format(url=url))
        self.id = id
        self.url = url
        self.progress_dicts = []

    def measure(self):
        return self._get_youtube_download_result(self.url)

    def _get_youtube_download_result(self, url):
        # Unique filename from process ID and timestamp
        file_dir = "{}/youtube-dl_{}".format(tempfile.gettempdir(), os.getpid())
        filename = "{}/youtube-dl_{}/{}".format(
            tempfile.gettempdir(), os.getpid(), int(time.time())
        )
        params = {
            "quiet": True,
            "no_progress": True,
            "progress_hooks": [self._store_progress_dicts_hook],
            "outtmpl": filename,
        }
        ydl = yt_dlp.YoutubeDL(params=params)
        try:
            ydl.extract_info(url)
        except yt_dlp.utils.ExtractorError as e:
            return self._get_youtube_download_error(
                "youtube-extractor", traceback=str(e)
            )
        except yt_dlp.utils.DownloadError as e:
            return self._get_youtube_download_error(
                "youtube-download", traceback=str(e)
            )
        try:
            # Extract size and duration from final progress step
            download_size = self.progress_dicts[-1]["total_bytes"]
            elapsed_time = self.progress_dicts[-1]["elapsed"]

            # Speed is only reported in non-final steps
            download_rate = self.progress_dicts[-2]["speed"] * 8
        except KeyError:
            return self._get_youtube_download_error(
                "youtube-attribute", traceback=str(self.progress_dicts)
            )
        except IndexError:
            return self._get_youtube_download_error(
                "youtube-progress_length", traceback=str(self.progress_dicts)
            )

        try:
            # Remove the created temp directory and all contents
            shutil.rmtree(file_dir)
        except FileNotFoundError as e:
            return self._get_youtube_download_error(
                "youtube-no_directory", traceback=str(e)
            )

        return YoutubeDownloadMeasurementResult(
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

    def _store_progress_dicts_hook(self, s):
        """
        Saves the results of the download progress to a list for later parsing.
        This function is called at every progress step in the download utility
        """
        self.progress_dicts.append(s)

    def _get_youtube_download_error(self, key, traceback):
        return YoutubeDownloadMeasurementResult(
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
