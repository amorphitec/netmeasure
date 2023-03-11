"""
Using the netflix_fast v2 api, the test collects some details about the client, and launches 1 thread per provided URL to download. Every `sleep_seconds` (presently 0.2) the test will append the latest speed (calculated by total downloaded bytes/total time taken) before checking for, in order:
    - `max_time_seconds` (presently 30s) expired.
    - Results have become "stabilised"
    - All threads have finished downloading
    - A single thread has finished downloading, IF `terminate_on_thread_complete=True`

Stabilisation is considered to be:
    - Downloaded has been running longer than `MIN_TIME_SECONDS` (presently 3s)
    - AND more than or equal to `MEASUREMENTS_COUNTED_BEFORE_CONSIDERED_STABLE` (presently 6) have been recorded
    - AND maximum percentage delta in these measurements is `< STABLE_MEASUREMENTS_DELTA` presently (2%)

In cases where the test concludes independently of the main loop (i.e when `reason_terminated == "thread_complete"`) The speed at the instant the thread completes is used, otherwise the final speed is used.

All this is then packaged into a `NetflixFastMeasurementResult`

After this, each of the URLs downloaded from has a latency test then have an Honesty-Box LatencyMeasurement test run against them, the results of which, along with the location and download rates/sizes for each thread are put into a `NetflixFastThreadResult`.

All these results are then returned as a list.
"""

import requests
import re
import time
import urllib
import json
from threading import Thread
from collections import deque
from statistics import mean

from netmeasure.measurements.base.measurements import BaseMeasurement
from netmeasure.measurements.base.results import Error
from netmeasure.units import RatioUnit, TimeUnit, StorageUnit, NetworkUnit
from netmeasure.measurements.latency.measurements import LatencyMeasurement
from netmeasure.measurements.file_download.measurements import FileDownloadMeasurement
from netmeasure.measurements.netflix_fast.results import (
    NetflixFastMeasurementResult,
    NetflixFastThreadResult,
)


NETFLIX_ERRORS = {
    "netflix-err": "Netflix test encountered an unknown error",
    "netflix-ping": "Netflix test encountered an error when pinging hosts",
    "netflix-response": "Netflix test received an invalid response from fast.com",
    "netflix-script-regex": "Netflix test failed to find script in the response",
    "netflix-script-response": "Netflix test received an invalid response from script",
    "netflix-token-regex": "Netflix test failed to find token in the response",
    "netflix-api-response": "Netflix test received an invalid response when querying for URLs",
    "netflix-api-json": "Netflix test failed to decode URLs",
    "netflix-api-parse": "Netflix test failed interpret elements of the decoded JSON",
    "netflix-connection": "Netflix test failed to connect to download URLs",
    "netflix-download": "Netflix test encountered an error downloading data",
}
MIN_TIME_SECONDS = 3
PING_COUNT = 4
MEASUREMENTS_COUNTED_BEFORE_CONSIDERED_STABLE = 6
STABLE_MEASUREMENTS_DELTA = 2
BITS_PER_BYTE = 8


class NetflixFastMeasurement(BaseMeasurement):
    def __init__(
        self,
        id,
        urlcount=3,
        max_time_seconds=30,
        sleep_seconds=0.2,
        chunk_size=64 * 2**10,
        terminate_on_thread_complete=True,
        terminate_on_result_stable=False,
    ):
        super(NetflixFastMeasurement, self).__init__(id=id)
        self.id = id
        self.urlcount = urlcount
        self.max_time_seconds = max_time_seconds
        self.sleep_seconds = sleep_seconds
        self.chunk_size = chunk_size
        self.terminate_on_thread_complete = terminate_on_thread_complete
        self.terminate_on_result_stable = terminate_on_result_stable
        self.finished_threads = 0
        self.exit_threads = False
        self.total = 0
        self.sessions = []
        self.client_data = {"asn": None, "ip": None, "isp": None, "location": None}
        self.targets = []
        self.thread_results = []
        self.completed_total = 0
        self.completed_elapsed_time = None

    def measure(self):
        results = []
        # Generate thread results dict structure
        for i in range(self.urlcount):
            self.thread_results.append(
                {
                    "index": i,
                    "elapsed_time": None,
                    "download_size": 0,
                    "download_rate": 0,
                    "url": None,
                    "location": None,
                }
            )

        results.append(self._get_fast_result())
        for thread_result in self.thread_results:
            results = results + self._get_url_result(thread_result)
        return results

    def _get_fast_result(self):
        s = requests.Session()
        try:
            resp = self._get_response(s)
        except ConnectionError as e:
            return self._get_netflix_error("netflix-response", traceback=str(e))

        try:
            script = re.search(r'<script src="(.*?)">', resp.text).group(1)
        except AttributeError:
            return self._get_netflix_error("netflix-script-regex", traceback=resp.text)

        try:
            script_resp = s.get("https://fast.com{script}".format(script=script))
        except ConnectionError as e:
            return self._get_netflix_error("netflix-script-response", traceback=str(e))

        try:
            token = re.search(r'token:"(.*?)"', script_resp.text).group(1)
        except AttributeError:
            return self._get_netflix_error(
                "netflix-token-regex", traceback=script_resp.text
            )

        try:
            self._query_api(s, token)
        except ConnectionError as e:
            return self._get_netflix_error("netflix-api-response", traceback=str(e))
        except json.decoder.JSONDecodeError as e:
            return self._get_netflix_error("netflix-api-json", traceback=str(e))
        except TypeError as e:
            return self._get_netflix_error("netflix-api-parse", traceback=str(e))
        except KeyError as e:
            return self._get_netflix_error("netflix-api-parse", traceback=str(e))

        try:
            conns = [
                self._get_connection(target["url"]) for target in self.thread_results
            ]
        except ConnectionError as e:
            return self._get_netflix_error("netflix-connection", traceback=str(e))

        fast_data = self._manage_threads(conns)

        return NetflixFastMeasurementResult(
            id=self.id,
            download_rate=float(fast_data["speed_bits"]),
            download_rate_unit=NetworkUnit("bit/s"),
            download_size=float(fast_data["total"]),
            download_size_unit=StorageUnit("B"),
            asn=self.client_data["asn"],
            ip=self.client_data["ip"],
            isp=self.client_data["isp"],
            city=self.client_data["location"]["city"],
            country=self.client_data["location"]["country"],
            urlcount=self.urlcount,
            reason_terminated=fast_data["reason_terminated"],
            errors=[],
        )

    def _manage_threads(self, conns):
        # Create worker threads
        threads = [None] * len(self.thread_results)
        for i in range(len(self.thread_results)):
            threads[i] = Thread(
                target=self._threaded_download,
                args=(conns[i], self.thread_results[i], time.time()),
            )
            threads[i].daemon = True
            threads[i].start()

        # Record approximate time
        start_time = time.time()
        recent_measurements = deque(
            maxlen=MEASUREMENTS_COUNTED_BEFORE_CONSIDERED_STABLE
        )
        recent_percent_deltas = deque(
            maxlen=MEASUREMENTS_COUNTED_BEFORE_CONSIDERED_STABLE
        )
        while True:
            elapsed_time = time.time() - start_time
            total = 0
            for thread_result in self.thread_results:
                total += thread_result["download_size"]
            speed_bits = total / elapsed_time * BITS_PER_BYTE
            recent_measurements.append(speed_bits)

            if (
                len(recent_measurements)
                == MEASUREMENTS_COUNTED_BEFORE_CONSIDERED_STABLE
            ):
                # Calculate percentage difference to the average of the last ten measurements
                # Note that there is no outlier detection here, all measurements are treated as-is.
                recent_percent_deltas.append(
                    (speed_bits - mean(recent_measurements)) / speed_bits * 100
                )

            if self._is_test_complete(elapsed_time, recent_percent_deltas):
                reason_terminated = self._is_test_complete(
                    elapsed_time, recent_percent_deltas
                )
                self.exit_threads = True
                for thread in threads:
                    thread.join()

                if (self.completed_elapsed_time is not None) & (
                    reason_terminated == "thread_complete"
                ):
                    # Record the speed at the time the thread finished downloading
                    speed_bits = (
                        self.completed_total
                        / self.completed_elapsed_time
                        * BITS_PER_BYTE
                    )
                else:
                    elapsed_time = time.time() - start_time
                    speed_bits = total / elapsed_time * BITS_PER_BYTE

                return {
                    "speed_bits": speed_bits,
                    "total": total,
                    "reason_terminated": reason_terminated,
                }
            time.sleep(self.sleep_seconds)

    def _threaded_download(self, conn, thread_result, start_time):
        # Iterate through the URL content
        g = conn.iter_content(chunk_size=self.chunk_size)
        for chunk in g:
            if self.exit_threads:
                break
            thread_result["download_size"] += len(chunk)

        completed_time = time.time()
        elapsed_time = completed_time - start_time

        # If this is the first thread to complete, record the time and total at this point
        if self.completed_elapsed_time is None:
            self.completed_elapsed_time = elapsed_time
            for global_thread_result in self.thread_results:
                self.completed_total += global_thread_result["download_size"]

        thread_result["download_rate"] = (
            thread_result["download_size"] / elapsed_time * BITS_PER_BYTE
        )
        thread_result["elapsed_time"] = elapsed_time
        self.finished_threads += 1

    def _query_api(self, s, token):
        params = {"https": "true", "token": token, "urlCount": self.urlcount}
        # '/v2/' path returns all location data about the servers
        api_resp = s.get("https://api.fast.com/netflix/speedtest/v2", params=params)
        api_json = api_resp.json()
        for i in range(len(api_json["targets"])):
            self.thread_results[i]["url"] = api_json["targets"][i]["url"]
            self.thread_results[i]["location"] = api_json["targets"][i]["location"]
        self.client_data = api_json["client"]
        return

    def _is_stabilised(self, recent_percent_deltas, elapsed_time):
        return (
            elapsed_time > MIN_TIME_SECONDS
            and len(recent_percent_deltas)
            >= MEASUREMENTS_COUNTED_BEFORE_CONSIDERED_STABLE
            and max(recent_percent_deltas) < STABLE_MEASUREMENTS_DELTA
        )

    def _get_response(self, s):
        return s.get("http://fast.com/")

    def _get_connection(self, url):
        s = requests.Session()
        self.sessions.append(s)
        conn = s.get(url, stream=True)
        return conn

    def _is_test_complete(self, elapsed_time, recent_percent_deltas):
        if elapsed_time > self.max_time_seconds:
            return "time_expired"
        if (self.terminate_on_result_stable) & (
            self._is_stabilised(recent_percent_deltas, elapsed_time)
        ):
            return "result_stabilised"
        if self.finished_threads == len(self.thread_results):
            return "all_complete"
        if (self.terminate_on_thread_complete) & (self.finished_threads >= 1):
            return "thread_complete"
        return False

    def _get_url_result(self, thread_result):
        host = urllib.parse.urlparse(thread_result["url"]).netloc
        city = thread_result["location"]["city"]
        country = thread_result["location"]["country"]
        LatencyResult = LatencyMeasurement(self.id, host, count=PING_COUNT).measure()[0]
        return [
            NetflixFastThreadResult(
                id=self.id,
                host=host,
                city=city,
                country=country,
                download_size=thread_result["download_size"],
                download_size_unit=StorageUnit("B"),
                download_rate=thread_result["download_rate"],
                download_rate_unit=NetworkUnit("bit/s"),
                elapsed_time=thread_result["elapsed_time"],
                elapsed_time_unit=TimeUnit("s"),
                errors=[],
            ),
            LatencyResult,
        ]

    def _get_netflix_error(self, key, traceback):
        return NetflixFastMeasurementResult(
            id=self.id,
            download_rate=None,
            download_rate_unit=None,
            download_size=None,
            download_size_unit=None,
            asn=None,
            ip=None,
            isp=None,
            city=None,
            country=None,
            urlcount=self.urlcount,
            reason_terminated=None,
            errors=[
                Error(
                    key=key,
                    description=NETFLIX_ERRORS.get(key, ""),
                    traceback=traceback,
                )
            ],
        )
