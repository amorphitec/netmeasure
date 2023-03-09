import uuid

import click
from exitstatus import ExitStatus

from .measurements.file_download.measurements import FileDownloadMeasurement

def get_uuid_str() -> str:
	"""
	Get a unique identifier string to assign to a measurement.
	"""
	return str(uuid.uuid4())

@click.group()
@click.option('-v', '--verbose', default=False, is_flag=True, required=False)
def cli(verbose):
    '''
    Run netmeasure as a cli application.
    '''
    return ExitStatus.success

@cli.command("file_download")
@click.option('-u', '--url', required=True, multiple=True, help="URL to download")
def run_file_download_measurement(url):
    """
    Perform a file download measurement.
    """
    measurement = FileDownloadMeasurement(
        id = get_uuid_str(),
        urls = url,
    )
    results = measurement.measure()
    # TODO: check for errors in results
    click.echo(results)
    return(results)
