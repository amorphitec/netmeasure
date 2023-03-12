import uuid

import click
from rich.console import Console
from rich.theme import Theme
from exitstatus import ExitStatus
from halo import Halo

from .measurements.file_download.measurements import FileDownloadMeasurement
from .measurements.file_download.results import FileDownloadMeasurementResult
from .measurements.ip_route.measurements import IPRouteMeasurement
from .measurements.ip_route.results import IPRouteMeasurementResult
from .measurements.latency.measurements import LatencyMeasurement
from .measurements.latency.results import LatencyMeasurementResult
from .measurements.netflix_fast.measurements import NetflixFastMeasurement
from .measurements.netflix_fast.results import NetflixFastMeasurementResult
from .measurements.netflix_fast.results import NetflixFastThreadResult
from .measurements.speedtest_dotnet.measurements import SpeedtestDotnetMeasurement
from .measurements.speedtest_dotnet.results import SpeedtestDotnetMeasurementResult
from .measurements.webpage_download.measurements import WebpageDownloadMeasurement
from .measurements.webpage_download.results import WebpageDownloadMeasurementResult
from .measurements.youtube_download.measurements import YoutubeDownloadMeasurement
from .measurements.youtube_download.results import YoutubeDownloadMeasurementResult


OUTPUT_THEME = Theme(
    {
        "info": "dim cyan",
        "warning": "magenta",
        "error": "bold red",
        "endpoint": "dim cyan",
        "value": "bold deep_sky_blue1",
        "unit": "white",
        "header": "bold white",
    }
)


def get_uuid_str() -> str:
    """
    Get a unique identifier string to assign to a measurement.
    """
    return str(uuid.uuid4())


@click.group(chain=True)
@click.option("-v", "--verbose", default=False, is_flag=True, required=False)
def cli(verbose):
    """
    Internet connection quality measurements.
    """
    pass


@cli.command("file_download")
@click.option(
    "-u", "--url", required=True, multiple=True, help="URL of file to download"
)
def perform_file_download_measurement(url):
    """
    Perform a file download measurement.

    Determines the URL with the lowest latency and then downloads it using wget.
    """

    console = Console(theme=OUTPUT_THEME)
    try:
        measurement = FileDownloadMeasurement(
            id=get_uuid_str(),
            urls=url,
        )
    except ValueError as err:
        raise click.BadParameter(err)
    with Halo(text="Performing File Download measurement", spinner="dots"):
        results = measurement.measure()
    output = f""
    for result in [r for r in results if type(r) == FileDownloadMeasurementResult]:
        if len(result.errors) > 0:
            for error in result.errors:
                console.print(f"[error]Error:[/error] {error.description}")
            return ExitStatus.failure
        output += (
            f"[header]:floppy_disk:  File Download   :floppy_disk:[/header]\n"
            f"URL: [endpoint]{result.url}[/endpoint]\n"
            f"Download Rate: [value]{result.download_rate}[/value] [unit]{result.download_rate_unit.value}[/unit] | "
            f"Download Size: [value]{result.download_size}[/value] [unit]{result.download_size_unit.value}[/unit]"
        )
    console.rule()
    console.print(output)
    console.rule()
    return ExitStatus.success


@cli.command("ip_route")
@click.option(
    "-h", "--host", required=True, multiple=True, help="Host to measure ip route to"
)
def perform_ip_route_measurement(host):
    """
    Perform an ip route measurement.

    Determines the host with the lowest latency and then measures the route to it.
    """

    console = Console(theme=OUTPUT_THEME)
    try:
        measurement = IPRouteMeasurement(
            id=get_uuid_str(),
            hosts=host,
        )
    except ValueError as err:
        raise click.BadParameter(err)
    with Halo(text="Performing IP Route measurement", spinner="dots"):
        results = measurement.measure()
    output = f""
    for result in [r for r in results if type(r) == IPRouteMeasurementResult]:
        if len(result.errors) > 0:
            for error in result.errors:
                console.print(f"[error]Error:[/error] {error.description}")
            return ExitStatus.failure
        output += (
            f"[header]:world_map:     IP Route     :world_map:[/header]\n"
            f"Host: [endpoint]{result.host}[/endpoint] | "
            f"IP: [endpoint]{result.ip}[/endpoint]\n"
            f"Route: [value]{', '.join(result.route)}[/value]\n"
            f"Hops: [value]{result.hop_count}[/value]"
        )
    console.rule()
    console.print(output)
    console.rule()
    return ExitStatus.success


@cli.command("latency")
@click.option(
    "-h", "--host", required=True, multiple=False, help="Host to measure latency to"
)
@click.option(
    "-c",
    "--count",
    default=3,
    required=False,
    multiple=False,
    help="Count of pings to send",
)
def perform_latency_measurement(host, count):
    """
    Perform a latency measurement.
    """

    console = Console(theme=OUTPUT_THEME)
    try:
        measurement = LatencyMeasurement(
            id=get_uuid_str(),
            host=host,
            count=count,
        )
    except ValueError as err:
        raise click.BadParameter(err)
    with Halo(text="Performing Latency measurement", spinner="dots"):
        results = measurement.measure()
    output = f"[header]:table_tennis_paddle_and_ball:     Latency     :table_tennis_paddle_and_ball:[/header]\n"
    for result in [r for r in results if type(r) == LatencyMeasurementResult]:
        if len(result.errors) > 0:
            for error in result.errors:
                console.print(f"[error]Error:[/error] {error.description}")
                return ExitStatus.failure
        output += (
            f"Host: [endpoint]{result.host}[/endpoint]\n"
            f"Minimum Latency: [value]{result.minimum_latency}[/value] [unit]{result.elapsed_time_unit.value}[/unit] | "
            f"Average Latency: [value]{result.average_latency}[/value] [unit]{result.elapsed_time_unit.value}[/unit] | "
            f"Maximum Latency: [value]{result.maximum_latency}[/value] [unit]{result.elapsed_time_unit.value}[/unit] | "
            f"Median Deviation: [value]{result.median_deviation}[/value] [unit]{result.elapsed_time_unit.value}[/unit]\n"
            f"Packets Transmitted: [value]{result.packets_transmitted}[/value] | "
            f"Packets Received: [value]{result.packets_transmitted}[/value] | "
            f"Packets Lost: [value]{result.packets_lost}[/value] [unit]{result.packets_lost_unit.value}[/unit]\n"
            f"Elapsed Time: [value]{result.elapsed_time}[/value] [unit]{result.elapsed_time_unit.value}[/unit]"
        )
    console.rule()
    console.print(output)
    console.rule()
    return ExitStatus.success


@cli.command("netflix_fast")
def perform_netflix_fast_measurement():
    """
    Perform a Netflix fast.com measurement.
    """

    console = Console(theme=OUTPUT_THEME)
    try:
        measurement = NetflixFastMeasurement(
            id=get_uuid_str(),
        )
    except ValueError as err:
        raise click.BadParameter(err)
    with Halo(text="Performing Netflix Fast measurement", spinner="dots"):
        results = measurement.measure()
    # Extract host details from thread results
    output = "[header]:popcorn:   Netflix Fast   :popcorn:[/header]\n"
    for index, result in enumerate(
        [r for r in results if type(r) == NetflixFastThreadResult]
    ):
        if len(result.errors) > 0:
            for error in result.errors:
                console.print(f"[error]Error:[/error] {error.description}")
            return ExitStatus.failure
        output += (
            f"Host {index}: [value]{result.host}[/value] | "
            f"Country: [value]{result.country}[/value] | "
            f"City: [value]{result.city}[/value]\n"
        )
    for result in [r for r in results if type(r) == NetflixFastMeasurementResult]:
        if len(result.errors) > 0:
            for error in result.errors:
                console.print(f"[error]Error:[/error] {error.description}")
        output += (
            f"Download Rate: [value]{result.download_rate}[/value] [unit]{result.download_rate_unit.value}[/unit] | "
            f"Download Size: [value]{result.download_size}[/value] [unit]{result.download_size_unit.value}[/unit]"
        )
    console.rule()
    console.print(output)
    console.rule()
    return ExitStatus.success


@cli.command("speedtest_dotnet")
def perform_speedtest_dotnet_measurement():
    """
    Perform a speedtest.net measurement.
    """

    console = Console(theme=OUTPUT_THEME)
    try:
        measurement = SpeedtestDotnetMeasurement(
            id=get_uuid_str(),
        )
    except ValueError as err:
        raise click.BadParameter(err)
    with Halo(text="Performing Speedtest Dotnet measurement", spinner="dots"):
        result = measurement.measure()
    if len(result.errors) > 0:
        for error in result.errors:
            console.print(f"[error]Error:[/error] {error.description}")
            return ExitStatus.failure
    output = (
        f"[header]:zap: Speedtest Dotnet :zap:[/header]\n"
        f"Host: [endpoint]{result.server_host}[/endpoint] | "
        f"Name: [value]{result.server_name}[/value] | "
        f"ID: [value]{result.server_id}[/value] | "
        f"Sponsor: [value]{result.server_sponsor}[/value]\n"
        f"Download Rate: [value]{result.download_rate}[/value] [unit]{result.download_rate_unit.value}[/unit] | "
        f"Upload Rate: [value]{result.upload_rate}[/value] [unit]{result.upload_rate_unit.value}[/unit]"
    )
    console.rule()
    console.print(output)
    console.rule()
    return ExitStatus.success


@cli.command("webpage_download")
@click.option(
    "-u", "--url", required=True, multiple=False, help="URL of webpage to download"
)
def perform_webpage_download_measurement(url):
    """
    Perform a webpage download measurement.
    """

    console = Console(theme=OUTPUT_THEME)
    try:
        measurement = WebpageDownloadMeasurement(
            id=get_uuid_str(),
            url=url,
        )
    except ValueError as err:
        raise click.BadParameter(err)
    with Halo(text="Performing Webpage Download measurement", spinner="dots"):
        result = measurement.measure()
    if len(result.errors) > 0:
        for error in result.errors:
            console.print(f"[error]Error:[/error] {error.description}")
            return ExitStatus.failure
    output = (
        f"[header]:globe_with_meridians: Webpage Download :globe_with_meridians:[/header]\n"
        f"URL: [endpoint]{result.url}[/endpoint]\n"
        f"Download Rate: [value]{result.download_rate}[/value] [unit]{result.download_rate_unit.value}[/unit] | "
        f"Download Size: [value]{result.download_size}[/value] [unit]{result.download_size_unit.value}[/unit]\n"
        f"Elapsed Time: [value]{result.elapsed_time}[/value] [unit]{result.elapsed_time_unit.value}[/unit] | "
        f"Asset Count: [value]{result.asset_count}[/value] | "
        f"Failed Asset Downloads: [value]{result.failed_asset_downloads}[/value]"
    )
    console.rule()
    console.print(output)
    console.rule()
    return ExitStatus.success


@cli.command("youtube_download")
@click.option(
    "-u",
    "--url",
    required=True,
    multiple=False,
    help="URL of YouTube video to download",
)
def perform_youtube_download_measurement(url):
    """
    Perform a youtube download measurement.
    """
    console = Console(theme=OUTPUT_THEME)
    try:
        measurement = YoutubeDownloadMeasurement(
            id=get_uuid_str(),
            url=url,
        )
    except ValueError as err:
        raise click.BadParameter(err)
    with Halo(text="Performing Youtube Download measurement", spinner="dots"):
        result = measurement.measure()
    if len(result.errors) > 0:
        for error in result.errors:
            console.print(f"[error]Error:[/error] {error.description}")
    output = (
        f"[header]:tv: Youtube Download :tv:[/header]\n"
        f"URL: [endpoint]{result.url}[/endpoint]\n"
        f"Download Rate: [value]{result.download_rate}[/value] [unit]{result.download_rate_unit.value}[/unit] | "
        f"Download Size: [value]{result.download_size}[/value] [unit]{result.download_size_unit.value}[/unit]\n"
        f"Elapsed Time: [value]{result.elapsed_time}[/value] [unit]{result.elapsed_time_unit.value}[/unit]"
    )
    console.rule()
    console.print(output)
    console.rule()
    return ExitStatus.success
