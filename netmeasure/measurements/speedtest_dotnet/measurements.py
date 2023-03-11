import re
import subprocess

import validators
from validators import ValidationFailure
import speedtest

from netmeasure.measurements.base.measurements import BaseMeasurement
from netmeasure.measurements.speedtest_dotnet.results import (
    SpeedtestDotnetMeasurementResult,
)
from netmeasure.measurements.base.results import Error
from netmeasure.units import RatioUnit, TimeUnit, StorageUnit, NetworkUnit

SPEEDTEST_ERRORS = {
    "speedtest-err": "wget had an unknown error.",
    "speedtest-config": "speedtest failed to retrieve a config",
    "speedtest-best-server": "speedtest could not find the best server",
    "speedtest-share": "speedtest could not share results",
    "speedtest-convert": "could not convert result values",
}


class SpeedtestDotnetMeasurement(BaseMeasurement):
    def __init__(self, id, servers=None):
        super(SpeedtestDotnetMeasurement, self).__init__(id=id)
        self.id = id
        self.servers = servers

    def measure(self, share=False):
        """
        @params share: Boolean determining whether to generate a PNG on speedtest.net displaying the result of the test.
        """
        try:
            s = speedtest.Speedtest()
        except speedtest.ConfigRetrievalError as e:
            return self._get_speedtest_error("speedtest-config", traceback=str(e))

        s.get_servers(self.servers)

        try:
            s.get_best_server()
        except speedtest.SpeedtestBestServerFailure as e:
            return self._get_speedtest_error("speedtest-best-server", traceback=str(e))

        s.download()
        s.upload()

        if share:
            try:
                s.results.share()
            except speedtest.ShareResultsConnectFailure as e:
                return self._get_speedtest_error("speedtest-share", traceback=str(e))

        results_dict = s.results.dict()
        try:
            return SpeedtestDotnetMeasurementResult(
                id=self.id,
                download_rate=float(results_dict["download"]),
                download_rate_unit=NetworkUnit("bit/s"),
                upload_rate=float(results_dict["upload"]),
                upload_rate_unit=NetworkUnit("bit/s"),
                data_received=(results_dict["bytes_received"]),
                data_received_unit=StorageUnit("B"),
                latency=float(results_dict["ping"]),
                server_name=results_dict["server"]["name"],
                server_id=results_dict["server"]["id"],
                server_sponsor=results_dict["server"]["sponsor"],
                server_host=results_dict["server"]["host"],
                errors=[],
            )
        except ValueError as e:
            return self._get_speedtest_error("speedtest-convert", traceback=str(e))

    def _get_speedtest_error(self, key, traceback):
        return SpeedtestDotnetMeasurementResult(
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
                    key=key,
                    description=SPEEDTEST_ERRORS.get(key, ""),
                    traceback=traceback,
                )
            ],
        )
