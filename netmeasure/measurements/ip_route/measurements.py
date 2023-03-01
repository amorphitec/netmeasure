"""
ip_route measurement, formerly the Traceroute measurement.
In a similar manner to the download_test, a list of hosts can be passed, in which case the one with the lowest latency is chosen.
The results are returned in order as:
 - IPRouteMeasurementResult
 - LatencyResult of the host used to create the IPRouteMeasurement
 - The LatencyResults from determining the initial latency
Traceroute measurement is provided by the "scapy" library. Note that this library needs route privileges to create
raw sockets, or to have the CAP_NET_RAW capability set.

"""
import socket
import validators
from validators import ValidationFailure

# Both of these imports seem to be required in order to mock the traceroute function
import scapy
from scapy.layers.inet import traceroute


from netmeasure.measurements.base.measurements import BaseMeasurement
from netmeasure.measurements.base.results import Error
from netmeasure.measurements.ip_route.results import IPRouteMeasurementResult
from netmeasure.measurements.latency.measurements import LatencyMeasurement

ROUTE_ERRORS = {
    "route-err": "iproute encountered an unknown error",
    "route-address": "iproute failed to find socket address",
    "route-permission": "iproute does not have permission to create a raw socket",
}


class IPRouteMeasurement(BaseMeasurement):
    def __init__(self, id, hosts, route_timeout=10, count=4):
        super(IPRouteMeasurement, self).__init__(id=id)

        if len(hosts) < 1:
            raise ValueError("At least one host must be provided.")
        for host in hosts:
            validated_domain = validators.domain(host)
            validated_ip = validators.ipv4(host)
            if isinstance(validated_domain, ValidationFailure) & isinstance(
                validated_ip, ValidationFailure
            ):
                raise ValueError("`{host}` is not a valid host".format(host=host))

        if count < 0:
            raise ValueError(
                "A value of {count} was provided for the number of pings. This must be a positive "
                "integer or `0` to turn off the ping.".format(count=count)
            )

        self.id = id
        self.hosts = hosts
        self.route_timeout = route_timeout
        self.count = count

    def measure(self):
        initial_latency_results = self._find_least_latent_host(self.hosts)
        least_latent_host = initial_latency_results[0][0]
        results = [self._get_traceroute_result(least_latent_host)]
        if self.count > 0:
            latency_measurement = LatencyMeasurement(
                self.id, least_latent_host, count=self.count
            )
            results.append(latency_measurement.measure()[0])
        results.extend([res for _, res in initial_latency_results])
        return results

    def _find_least_latent_host(self, hosts):
        """
        Performs a latency test for each specified host
        Returns a sorted list of LatencyResults, sorted by average latency
        """
        initial_latency_results = []
        for host in hosts:
            latency_measurement = LatencyMeasurement(self.id, host, count=2)
            initial_latency_results.append((host, latency_measurement.measure()[0]))
        return sorted(
            initial_latency_results,
            key=lambda x: (x[1].average_latency is None, x[1].average_latency),
        )

    def _get_traceroute_result(self, host):
        try:
            # Test whether raw socket privileges exist:
            socket.socket(socket.AF_PACKET, socket.SOCK_RAW)

            # Commence traceroute test:
            traceroute_out = scapy.layers.inet.traceroute(host, verbose=0)
            traceroute_trace = traceroute_out[0].get_trace()
            ip = list(traceroute_trace.keys())[0]
            hop_count = len(traceroute_trace[ip])
            trace_list = [
                x[0] for x in traceroute_trace[ip].values()
            ]  # Reshape dict into list of ips
        except socket.gaierror as e:
            return self._get_ip_route_error("route-address", traceback=str(e))
        except PermissionError as e:
            return self._get_ip_route_error("route-permission", traceback=str(e))

        return IPRouteMeasurementResult(
            id=self.id,
            host=host,
            ip=ip,
            hop_count=hop_count,
            route=trace_list,
            errors=[],
        )

    def _get_ip_route_error(self, key, traceback):
        return IPRouteMeasurementResult(
            id=self.id,
            host=None,
            ip=None,
            hop_count=None,
            route=None,
            errors=[
                Error(
                    key=key, description=ROUTE_ERRORS.get(key, ""), traceback=traceback
                )
            ],
        )
