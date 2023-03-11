## Unreleased

## [1.2.0] (2022-03-11)

### Added
- Add webpage measurement
- Measurement details to README
- CLI for all measurements

### Changed
- Separate netflix_fast LatencyMeasurement into a new result
- Change `time`
- Rename youtube measurement to youtube download
- Rename speedtestdotnet measurement to speedtest dotnet
- Rename download speed measurement to file download
- Restructure project

### Fixed
- Inconsistent storage unit names
- Github actions

### Removed
- Support for Python 3.7

## [1.1.0] (2020-08-23)

### Changed
- Rename trace to route in ip_route result

### Added
- Add data_received to speedtestdotnet measurement

## [1.0.10] (2020-08-19)

### Fixed
- Fix IP route measurement permissions

## [1.0.9] (2020-08-18)

### Fixed
- Fix scapy defined as dev dependency

## [1.0.8] (2020-08-14)

### Added
- Add youtube measurement

## [1.0.7] (2020-08-10)

### Added
- Add IP route measurement
- Allow IPs as hosts for LatencyMeasurement

## [1.0.6] (2020-06-23)

### Added
- Add netflixfast measurement
- Add test run on review request

## [1.0.5] (2020-05-06)

### Changed
- Updated dependencies

### Fixed
- Fix speedtestdotnet error on Python 3.5

## [1.0.4] (2020-04-09)

### Fixed
- Change speedtestdotnet namedtuple fields

## [1.0.3] (2020-03-16)

### Added
- Add speedtestdotnet measurement
### Fixed
- Change poetry dataclasses version

## [1.0.2] (2019-11-19)

### Added
- Add detailed ping measurement

## [1.0.1] (2019-11-13)

### Added
- Update `pyproject.toml` metadata

## [1.0.0]

### Added
- Initial release
