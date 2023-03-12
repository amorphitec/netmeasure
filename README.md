[![PyPI version](https://badge.fury.io/py/netmeasure.svg)](https://badge.fury.io/py/netmeasure)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/netmeasure.svg)](https://pypi.python.org/pypi/netmeasure/)
[![GitHub license](https://img.shields.io/github/license/amorphitec/netmeasure)](https://github.com/amorhpitec/netmeaure/blob/master/LICENSE)
[![GitHub Actions (Tests)](https://github.com/amorphitec/netmeasure/workflows/Tests/badge.svg)](https://github.com/amorphitec/netmeasure)

# Netmeasure

A library for measuring Internet connection quality in a structured and consistent way.

[![asciinema_netmeasure_v1.2.5](https://asciinema.org/a/rHagzsiXoDxxyBtkdTV77chta.svg)](https://asciinema.org/a/rHagzsiXoDxxyBtkdTV77chta)

## Purpose

There are a variety of services, clients, tools, and methodologies used to measure Internet connection quality. Each of these has its own advantages, flaws, biases and units of measurement.

Netmeasure brings together a variety of Internet connection quality measurements in a single library with a consistent interface and explicitly-defined units.

An open-source license ensures methodology is transparent and open to ongoing community improvement.

## Measurements

- `file_download` - measures download of a file from a given endpoint using the [wget](https://www.gnu.org/software/wget/) application.
- `ip_route` - measures network hops to a given endpoint using the [scapy](https://scapy.net/) library.
- `latency` - measures latency to a given endpoint using the [ping](https://en.wikipedia.org/wiki/Ping_%28networking_utility%29) application.
- `netflix_fast` - measures download from the [netflix fast](https://fast.com/) service using the [requests](https://requests.readthedocs.io/en/latest/) library.
- `speedtest_dotnet` - measures download from, upload to and latency to the [speedtest.net](https://www.speedtest.net/) service using the [speedtest-cli](https://pypi.org/project/speedtest-cli/) library.
- `webpage_download` - measures download of a given web page and its associated assets using the [requests](https://requests.readthedocs.io/en/latest/) library.
- `youtube_download` - measures download of a given [youtube](https://www.youtube.com/) video using the [youtube-dl](https://youtube-dl.org/) library.

## Usage

...

## Requirements

`netmeasure` supports Python 3.8 to Python 3.11 inclusively.

## Development

### Git hooks

[pre-commit](https://pre-commit.com/) hooks are included to ensure code quality
on `commit` and `push`. Install these hooks like so:

```shell script
$ pre-commit install && pre-commit install -t pre-push
asd
```

### Publishing a release

1. Install [poetry](https://poetry.eustace.io)

2. Checkout the release:

    ```shell script
    $ git checkout v<x>.<y>.<z>
    ```

3. Publish the release:

    ```shell script
    $ poetry publish --build
    ```
