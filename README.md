[![PyPI version](https://badge.fury.io/py/netmeasure.svg)](https://badge.fury.io/py/netmeasure)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/netmeasure.svg)](https://pypi.python.org/pypi/netmeasure/)
[![GitHub license](https://img.shields.io/github/license/amorphitec/netmeasure)](https://github.com/amorhpitec/netmeaure/blob/master/LICENSE)
[![GitHub Actions (Tests)](https://github.com/amorphitec/netmeasure/workflows/Tests/badge.svg)](https://github.com/amorphitec/netmeasure)

# Netmeasure

A CLI tool and Python library for measuring Internet connection quality in a structured and consistent way.

[![asciinema_netmeasure_v1.2.5](https://asciinema.org/a/rHagzsiXoDxxyBtkdTV77chta.svg)](https://asciinema.org/a/rHagzsiXoDxxyBtkdTV77chta)

## Purpose

Many services, clients, tools, and methodologies exist to measure Internet connection quality. Each of these has particular advantages, flaws, biases and units of measurement.

`netmeasure` brings together a variety of Internet connection quality measurements in a single package, with a consistent interface and explicitly-defined units.

An open-source license ensures methodology is transparent and open to ongoing community improvement.

## Requirements

`netmeasure` supports Python 3.8 to Python 3.11 inclusively.

## CLI tool

`netmeasure` can be used to run measurements directly from the command line.

### Installation

Install with [pipx](https://pypa.github.io/pipx/getting-started/):

```shell script
$ pipx install netmeasure
```

### Usage

Use `netmeasure --help` to see a list of available measurements:

```shell script
Usage: netmeasure [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

  Internet connection quality measurements.

Options:
  -v, --verbose
  --help         Show this message and exit.

Commands:
  file_download     Perform a file download measurement.
  ip_route          Perform an ip route measurement.
  latency           Perform a latency measurement.
  netflix_fast      Perform a Netflix fast.com measurement.
  speedtest_dotnet  Perform a speedtest.net measurement.
  webpage_download  Perform a webpage download measurement.
  youtube_download  Perform a youtube download measurement.
```

Use `netmeasure <measurement> --help` for details for a specific measurement:

```shell script
netmeasure netflix_fast --help
Usage: netmeasure netflix_fast [OPTIONS]

  Perform a Netflix fast.com measurement.

Options:
  --help  Show this message and exit.
```

```shell script
$ netmeasure netflix_fast

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
🍿   Netflix Fast   🍿
Host 0: ipv4-c003-syd001-superloop-isp.1.oca.nflxvideo.net | Country: AU | City: Alexandria
Host 1: ipv4-c004-syd002-superloop-isp.1.oca.nflxvideo.net | Country: AU | City: Sydney
Host 2: ipv4-c001-meb002-superloop-isp.1.oca.nflxvideo.net | Country: AU | City: Port Melbourne
Download Rate: 25393008.677629545 bit/s | Download Size: 54657024.0 B
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

Measurements can be performed sequentially by chaining commands:

```shell script
$ netmeasure \
netflix_fast \
latency --host 1.1.1.1
speedtest_dotnet

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
🍿   Netflix Fast   🍿
Host 0: ipv4-c003-syd001-superloop-isp.1.oca.nflxvideo.net | Country: AU | City: Alexandria
Host 1: ipv4-c004-syd002-superloop-isp.1.oca.nflxvideo.net | Country: AU | City: Sydney
Host 2: ipv4-c001-meb002-superloop-isp.1.oca.nflxvideo.net | Country: AU | City: Port Melbourne
Download Rate: 25393008.677629545 bit/s | Download Size: 54657024.0 B
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
🏓     Latency     🏓
Host: 1.1.1.1
Minimum Latency: 4.403 ms | Average Latency: 107.408 ms | Maximum Latency: 313.408 ms |Median Deviation: 
145.663 ms
Packets Transmitted: 3 | Packets Received: 3 | Packets Lost: 0.0 %
Elapsed Time: 2002.0 ms
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
⚡ Speedtest Dotnet ⚡
Host: st-syd-02.gcomm.com.au:8080 | Name: Sydney | ID: 29570 | Sponsor: Nexon Asia Pacific
Download Rate: 25007776.530098625 bit/s | Upload Rate: 19202829.854627796 bit/s
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

## Library

`netmeasure` can be used as a library to run measurements and obtain structured results from within your application.

### Installation

Install from PyPI:

```shell script
$ pip install -U netmeasure

```

### Usage

```python
import uuid
from pprint import pprint

# Import the required measurement.
from netmeasure.measurements.latency.measurements import LatencyMeasurement

# Create a measurement.
# Note: A measurement requires an id. This id will be added to all results
# generated by this measurement instance.
my_latency_measurement = LatencyMeasurement(id=str(uuid.uuid4()), host='1.1.1.1')

# Run the measurement.
my_result = my_latency_measurement.measure()

# Print the measurement result(s)
pprint(my_result)
```

```python
[LatencyMeasurementResult(id='fb6f0c59-e6dc-4f3f-8139-c8b4b2d94871'),
	errors=[],
	host='1.1.1.1',
	minimum_latency=3.939,
	average_latency=4.195,
	maximum_latency=4.361,
	median_deviation=0.164,
	packets_transmitted=4,
	packets_received=4,
	packets_lost=0.0,
	packets_lost_unit=<RatioUnit.percentage: '%'>,
	elapsed_time=3004.0,
	elapsed_time_unit=<TimeUnit.millisecond: 'ms'>)]
```

Take a look at the commands defined in `netmeasure/cli.py` for more examples.

## Measurements

The following measurements are currently available:

- `file_download` - measures download of a file from a given endpoint using the [wget](https://www.gnu.org/software/wget/) application.
- `ip_route` - measures network hops to a given endpoint using the [scapy](https://scapy.net/) library.
- `latency` - measures latency to a given endpoint using the [ping](https://en.wikipedia.org/wiki/Ping_%28networking_utility%29) application.
- `netflix_fast` - measures download from the [netflix fast](https://fast.com/) service using the [requests](https://requests.readthedocs.io/en/latest/) library.
- `speedtest_dotnet` - measures download from, upload to and latency to the [speedtest.net](https://www.speedtest.net/) service using the [speedtest-cli](https://pypi.org/project/speedtest-cli/) library.
- `webpage_download` - measures download of a given web page and its associated assets using the [requests](https://requests.readthedocs.io/en/latest/) library.
- `youtube_download` - measures download of a given [youtube](https://www.youtube.com/) video using the [youtube-dl](https://youtube-dl.org/) library.

_Note: Some measurements require particular cli tools to be installed_

## Development

### Git hooks

[pre-commit](https://pre-commit.com/) hooks are included to ensure code quality
on `commit` and `push`. Install these hooks like so:

```shell script
$ pre-commit install && pre-commit install -t pre-push
```
