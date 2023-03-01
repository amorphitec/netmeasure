[![PyPI version](https://badge.fury.io/py/honestybox-measurement.svg)](https://badge.fury.io/py/honestybox-measurement)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/honestybox-measurement.svg)](https://pypi.python.org/pypi/honestybox-measurement/)
[![GitHub license](https://img.shields.io/github/license/honesty-box/honestybox-measurement)](https://github.com/honesty-box/honestybox-measurement/blob/master/LICENSE)
[![GitHub Actions (Tests)](https://github.com/honesty-box/honestybox-measurement/workflows/Tests/badge.svg)](https://github.com/honesty-box/honestybox-measurement)

# Netmeasure

A library for measuring Internet connection quality in a structured and consistent way.

## Purpose

There are a variety of services, clients, tools, and methodologies used to measure Internet connection quality. Each of these has its own advantages, flaws, biases and units of measurement.

Netmeasure brings these together in a single measurement library with a consistent interface and explicitly-defined units. Being open-source ensures transparent methodology and allows for ongoing community improvement.

## Usage

## Requirements

`netmeasurem` supports Python 3.7 to Python 3.11 inclusively.

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
