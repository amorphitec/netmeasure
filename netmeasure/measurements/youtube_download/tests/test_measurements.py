import sys
import json
from unittest import TestCase, mock

import yt_dlp

from netmeasure.measurements.youtube_download.measurements import (
    YoutubeDownloadMeasurement,
    YOUTUBE_ERRORS,
)
from netmeasure.measurements.youtube_download.results import (
    YoutubeDownloadMeasurementResult,
)
from netmeasure.measurements.latency.results import LatencyMeasurementResult
from netmeasure.measurements.base.results import Error
from netmeasure.units import RatioUnit, TimeUnit, StorageUnit, NetworkUnit

"""
Note that the constructors for the yt_dlp errors occasionally add their own text in addition to the passed message!
"""


class YoutubeDownloadResultTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.id = "1"
        self.test_url = "https://www.youtube.com/watch?v=1233zthJUf31MA"
        self.ytm = YoutubeDownloadMeasurement(self.id, self.test_url)
        self.mock_progress_dicts = [
            {
                "_eta_str": "Unknown ETA",
                "_percent_str": "  0.0%",
                "_speed_str": "Unknown speed",
                "_total_bytes_str": "123.4MiB",
                "downloaded_bytes": 1024,
                "elapsed": 0.13415765762329102,
                "eta": None,
                "filename": "/tmp/youtube-dl_7954/1596695025_Portland Protest.mp4",
                "speed": None,
                "status": "downloading",
                "tmpfilename": "/tmp/youtube-dl_31918/1234567890_Fake Video.mp4.part",
                "total_bytes": 163492702,
            },
            {
                "_eta_str": "00:00",
                "_percent_str": "100.0%",
                "_speed_str": "12.34MiB/s",
                "_total_bytes_str": "123.4MiB",
                "downloaded_bytes": 163492702,
                "elapsed": 13.792589902877808,
                "eta": 0,
                "filename": "/tmp/youtube-dl_31918/1596679305_Portland Protest.mp4",
                "speed": 12345678.012500000,
                "status": "downloading",
                "tmpfilename": "/tmp/youtube-dl_31918/1234567890_Fake Video.mp4.part",
                "total_bytes": 163492702,
            },
            {
                "_elapsed_str": "12:34",
                "_total_bytes_str": "123.4MiB",
                "downloaded_bytes": 123456789,
                "elapsed": 12.345678987654321,
                "filename": "/tmp/youtube-dl_31918/1234567890_Fake Video.mp4",
                "status": "finished",
                "total_bytes": 123456789,
            },
        ]
        self.mock_progress_dicts_missing_attribute = [
            {
                "_eta_str": "Unknown ETA",
                "_percent_str": "  0.0%",
                "_speed_str": "Unknown speed",
                "_total_bytes_str": "123.4MiB",
                "downloaded_bytes": 1024,
                "elapsed": 0.13415765762329102,
                "eta": None,
                "filename": "/tmp/youtube-dl_7954/1596695025_Portland Protest.mp4",
                "speed": None,
                "status": "downloading",
                "tmpfilename": "/tmp/youtube-dl_31918/1234567890_Fake Video.mp4.part",
                "total_bytes": 163492702,
            },
            {
                "_eta_str": "00:00",
                "_percent_str": "100.0%",
                "_speed_str": "12.34MiB/s",
                "_total_bytes_str": "123.4MiB",
                "downloaded_bytes": 163492702,
                "elapsed": 13.792589902877808,
                "eta": 0,
                "filename": "/tmp/youtube-dl_31918/1596679305_Portland Protest.mp4",
                "speed": 12345678.012500000,
                "status": "downloading",
                "tmpfilename": "/tmp/youtube-dl_31918/1234567890_Fake Video.mp4.part",
                "total_bytes": 163492702,
            },
            {
                "_elapsed_str": "12:34",
                "_total_bytes_str": "123.4MiB",
                "downloaded_bytes": 123456789,
                "elapsed": 12.345678987654321,
                "filename": "/tmp/youtube-dl_31918/1234567890_Fake Video.mp4",
                "status": "finished",
                "BADotal_bytes": 123456789,
            },
        ]
        self.mock_progress_dicts_only_final = [
            {
                "_elapsed_str": "12:34",
                "_total_bytes_str": "123.4MiB",
                "downloaded_bytes": 123456789,
                "elapsed": 12.345678987654321,
                "filename": "/tmp/youtube-dl_31918/1234567890_Fake Video.mp4",
                "status": "finished",
                "total_bytes": 123456789,
            }
        ]
        self.mock_valid_youtube_download_result = YoutubeDownloadMeasurementResult(
            id=self.id,
            url=self.test_url,
            download_rate=98765424.1,
            download_rate_unit=NetworkUnit("bit/s"),
            download_size=123456789,
            download_size_unit=StorageUnit("B"),
            elapsed_time=12.345678987654321,
            elapsed_time_unit=TimeUnit("s"),
            errors=[],
        )
        self.mock_extraction_fail_result = YoutubeDownloadMeasurementResult(
            id=self.id,
            url=self.test_url,
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            elapsed_time=None,
            elapsed_time_unit=None,
            errors=[
                Error(
                    key="youtube-extractor",
                    description=YOUTUBE_ERRORS.get("youtube-extractor", ""),
                    traceback="Extraction failed!; please report this issue on  https://github.com/yt-dlp/yt-dlp/issues?q= , filling out the appropriate issue template. Confirm you are on the latest version using  yt-dlp -U",
                )
            ],
        )
        self.mock_download_fail_result = YoutubeDownloadMeasurementResult(
            id=self.id,
            url=self.test_url,
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            elapsed_time=None,
            elapsed_time_unit=None,
            errors=[
                Error(
                    key="youtube-download",
                    description=YOUTUBE_ERRORS.get("youtube-download", ""),
                    traceback="Download failed!",
                )
            ],
        )
        self.mock_missing_attribute_result = YoutubeDownloadMeasurementResult(
            id=self.id,
            url=self.test_url,
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            elapsed_time=None,
            elapsed_time_unit=None,
            errors=[
                Error(
                    key="youtube-attribute",
                    description=YOUTUBE_ERRORS.get("youtube-attribute", ""),
                    traceback=str(self.mock_progress_dicts_missing_attribute),
                )
            ],
        )
        self.mock_final_only_result = (
            YoutubeDownloadMeasurementResult(
                id=self.id,
                url=self.test_url,
                download_rate=None,
                download_rate_unit=None,
                download_size=None,
                download_size_unit=None,
                elapsed_time=None,
                elapsed_time_unit=None,
                errors=[
                    Error(
                        key="youtube-progress_length",
                        description=YOUTUBE_ERRORS.get("youtube-progress_length", ""),
                        traceback=str(self.mock_progress_dicts_only_final),
                    )
                ],
            ),
        )
        self.mock_final_only_result = YoutubeDownloadMeasurementResult(
            id=self.id,
            url=self.test_url,
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            elapsed_time=None,
            elapsed_time_unit=None,
            errors=[
                Error(
                    key="youtube-progress_length",
                    description=YOUTUBE_ERRORS.get("youtube-progress_length", ""),
                    traceback=str(self.mock_progress_dicts_only_final),
                )
            ],
        )
        self.mock_file_remove_result = YoutubeDownloadMeasurementResult(
            id=self.id,
            url=self.test_url,
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            elapsed_time=None,
            elapsed_time_unit=None,
            errors=[
                Error(
                    key="youtube-file",
                    description=YOUTUBE_ERRORS.get("youtube-file", ""),
                    traceback="[Errno 2] No such file or directory: 'example_file'",
                )
            ],
        )
        self.mock_directory_remove_result = YoutubeDownloadMeasurementResult(
            id=self.id,
            url=self.test_url,
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            elapsed_time=None,
            elapsed_time_unit=None,
            errors=[
                Error(
                    key="youtube-no_directory",
                    description=YOUTUBE_ERRORS.get("youtube-no_directory", ""),
                    traceback="[Errno 2] No such file or directory: 'example_dir'",
                )
            ],
        )
        self.mock_directory_remove_nonempty_result = YoutubeDownloadMeasurementResult(
            id=self.id,
            url=self.test_url,
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            elapsed_time=None,
            elapsed_time_unit=None,
            errors=[
                Error(
                    key="youtube-directory_nonempty",
                    description=YOUTUBE_ERRORS.get("youtube-directory_nonempty", ""),
                    traceback="[Errno 39] Directory not empty: 'example_dir'",
                )
            ],
        )

    @mock.patch("shutil.rmtree")
    @mock.patch("os.remove")
    @mock.patch("os.rmdir")
    @mock.patch.object(yt_dlp, "YoutubeDL")
    def test_youtube_download_result_valid(
        self, mock_YoutubeDL, mock_rmdir, mock_remove, mock_rmtree
    ):
        self.ytm.progress_dicts = self.mock_progress_dicts
        mock_ydl = mock.MagicMock()
        mock_ydl.extract_info.return_value = None
        mock_YoutubeDL.return_value = mock_ydl
        mock_rmdir.side_effect = [0]
        mock_remove.side_effect = [0]
        mock_rmtree.side_effect = [0]
        self.assertEqual(
            self.ytm._get_youtube_download_result(self.test_url),
            self.mock_valid_youtube_download_result,
        )

    @mock.patch("shutil.rmtree")
    @mock.patch("os.remove")
    @mock.patch("os.rmdir")
    @mock.patch.object(yt_dlp, "YoutubeDL")
    def test_youtube_download_result_extraction_error(
        self, mock_YoutubeDL, mock_rmdir, mock_remove, mock_rmtree
    ):
        self.ytm.progress_dicts = self.mock_progress_dicts
        mock_ydl = mock.MagicMock()
        mock_ydl.extract_info.side_effect = [
            yt_dlp.utils.ExtractorError("Extraction failed!")
        ]
        mock_YoutubeDL.return_value = mock_ydl
        mock_rmdir.side_effect = [0]
        mock_remove.side_effect = [0]
        mock_rmtree.side_effect = [0]

        # print(self.ytm._get_youtube_download_result(self.test_url))
        # print(self.mock_extraction_fail_result)

        self.assertEqual(
            self.ytm._get_youtube_download_result(self.test_url),
            self.mock_extraction_fail_result,
        )

    @mock.patch("shutil.rmtree")
    @mock.patch("os.remove")
    @mock.patch("os.rmdir")
    @mock.patch.object(yt_dlp, "YoutubeDL")
    def test_youtube_download_result_download_error(
        self, mock_YoutubeDL, mock_rmdir, mock_remove, mock_rmtree
    ):
        self.ytm.progress_dicts = self.mock_progress_dicts
        mock_ydl = mock.MagicMock()
        mock_ydl.extract_info.side_effect = [
            yt_dlp.utils.DownloadError("Download failed!")
        ]
        mock_YoutubeDL.return_value = mock_ydl
        mock_rmdir.side_effect = [0]
        mock_remove.side_effect = [0]
        mock_rmtree.side_effect = [0]
        self.assertEqual(
            self.ytm._get_youtube_download_result(self.test_url),
            self.mock_download_fail_result,
        )

    @mock.patch("shutil.rmtree")
    @mock.patch("os.remove")
    @mock.patch("os.rmdir")
    @mock.patch.object(yt_dlp, "YoutubeDL")
    def test_youtube_download_result_attribute_error(
        self, mock_YoutubeDL, mock_rmdir, mock_remove, mock_rmtree
    ):
        self.ytm.progress_dicts = self.mock_progress_dicts_missing_attribute
        mock_ydl = mock.MagicMock()
        mock_ydl.extract_info.side_effect = None
        mock_YoutubeDL.return_value = mock_ydl
        mock_rmdir.side_effect = [0]
        mock_remove.side_effect = [0]
        mock_rmtree.side_effect = [0]
        self.assertEqual(
            self.ytm._get_youtube_download_result(self.test_url),
            self.mock_missing_attribute_result,
        )

    @mock.patch("shutil.rmtree")
    @mock.patch("os.remove")
    @mock.patch("os.rmdir")
    @mock.patch.object(yt_dlp, "YoutubeDL")
    def test_youtube_download_result_only_final_progress(
        self, mock_YoutubeDL, mock_rmdir, mock_remove, mock_rmtree
    ):
        self.ytm.progress_dicts = self.mock_progress_dicts_only_final
        mock_ydl = mock.MagicMock()
        mock_ydl.extract_info.side_effect = None
        mock_YoutubeDL.return_value = mock_ydl
        mock_rmdir.side_effect = [0]
        mock_remove.side_effect = [0]
        mock_rmtree.side_effect = [0]
        self.assertEqual(
            self.ytm._get_youtube_download_result(self.test_url),
            self.mock_final_only_result,
        )

    # NOTE: OUTDATED
    # @mock.patch("shutil.rmtree")
    # @mock.patch("os.remove")
    # @mock.patch("os.rmdir")
    # @mock.patch.object(yt_dlp, "YoutubeDL")
    # def test_youtube_download_result_remove_file(self, mock_YoutubeDL, mock_rmdir, mock_remove, mock_rmtree):
    #     self.ytm.progress_dicts = self.mock_progress_dicts
    #     mock_ydl = mock.MagicMock()
    #     mock_ydl.extract_info.side_effect = None
    #     mock_YoutubeDL.return_value = mock_ydl
    #     mock_rmdir.side_effect = [0]
    #     mock_remove.side_effect = [0]
    #     mock_rmtree.side_effect = [
    #         FileNotFoundError("[Errno 2] No such file or directory: 'example_file'")
    #     ]
    #     self.assertEqual(
    #         self.ytm._get_youtube_download_result(self.test_url), self.mock_file_remove_result
    #     )

    @mock.patch("shutil.rmtree")
    @mock.patch("os.remove")
    @mock.patch("os.rmdir")
    @mock.patch.object(yt_dlp, "YoutubeDL")
    def test_youtube_download_result_remove_directory(
        self, mock_YoutubeDL, mock_rmdir, mock_remove, mock_rmtree
    ):
        self.ytm.progress_dicts = self.mock_progress_dicts
        mock_ydl = mock.MagicMock()
        mock_ydl.extract_info.side_effect = None
        mock_YoutubeDL.return_value = mock_ydl
        mock_rmtree.side_effect = [
            FileNotFoundError("[Errno 2] No such file or directory: 'example_dir'")
        ]
        mock_rmdir.side_effect = [0]
        mock_remove.side_effect = [0]
        self.assertEqual(
            self.ytm._get_youtube_download_result(self.test_url),
            self.mock_directory_remove_result,
        )

    # NOTE: OUTDATED
    # @mock.patch("os.remove")
    # @mock.patch("os.rmdir")
    # @mock.patch.object(yt_dlp, "YoutubeDL")
    # def test_youtube_download_result_remove_directory_nonempty(
    #     self, mock_YoutubeDL, mock_rmdir, mock_remove
    # ):
    #     self.ytm.progress_dicts = self.mock_progress_dicts
    #     mock_ydl = mock.MagicMock()
    #     mock_ydl.extract_info.side_effect = None
    #     mock_YoutubeDL.return_value = mock_ydl
    #     mock_rmdir.side_effect = [
    #         OSError("[Errno 39] Directory not empty: 'example_dir'")
    #     ]
    #     mock_remove.side_effect = [0]
    #     self.assertEqual(
    #         self.ytm._get_youtube_download_result(self.test_url),
    #         self.mock_directory_remove_nonempty_result,
    #     )
