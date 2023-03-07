[![PyPI version](https://badge.fury.io/py/honestybox-measurement.svg)](https://badge.fury.io/py/honestybox-measurement)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/honestybox-measurement.svg)](https://pypi.python.org/pypi/honestybox-measurement/)
[![GitHub license](https://img.shields.io/github/license/honesty-box/honestybox-measurement)](https://github.com/honesty-box/honestybox-measurement/blob/master/LICENSE)
[![GitHub Actions (Tests)](https://github.com/honesty-box/honestybox-measurement/workflows/Tests/badge.svg)](https://github.com/honesty-box/honestybox-measurement)

# Netmeasure

A library for measuring Internet connection quality in a structured and consistent way.

## Purpose

There are a variety of services, clients, tools, and methodologies used to measure Internet connection quality. Each of these has its own advantages, flaws, biases and units of measurement.

Netmeasure brings together a variety of Internet connection quality measurements in a single library with a consistent interface and explicitly-defined units.

An open-source license ensures methodology is transparent and open to ongoing community improvement.

## Measurements

- `file_download` - measures download of a file from a given endpoint using the wget application
- `ip_route` - measures network hops to a given endpoint using the scapy library
- `latency` - measures latency to a given endpoint using the ping application
- `netflix_fast` - measures download from the netflix fast service using the requests library
- `speedtest_dotnet` - measures download from, upload to and latency to the speedtest.net service using the speedtest library
- `webpage_download` - measures download of a given web page and its associated assets using the requests library
- `youtube_download` - measures download of a given youtube video using the youtube-dl library

## Usage

...

## Requirements

`netmeasure` supports Python 3.7 to Python 3.11 inclusively.

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
