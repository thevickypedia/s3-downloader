import sys
from typing import Optional

import click

from s3.dumper import Downloader  # noqa: F401
from s3.logger import LogType

version = "1.0.1"


# noinspection PyUnusedLocal
@click.command()
@click.pass_context
@click.option(
    "-b",
    "--bucket",
    required=True,
    help="Bucket name to download from.",
)
@click.option(
    "-d",
    "--destination",
    required=False,
    help="Destination path to save the downloaded files.",
)
@click.option(
    "-p",
    "--prefix",
    required=False,
    help="Comma-separated list of prefixes to limit the objects to download.",
)
@click.option(
    "-w",
    "--workers",
    required=False,
    help="Number of workers to use for downloading files concurrently.",
)
@click.option(
    "-l",
    "--log",
    required=False,
    help="Number of workers to use for downloading files concurrently.",
)
def _cli(
        *args,
        bucket: str,
        destination: str,
        prefix: Optional[str],
        workers: Optional[str] = None,
        log: Optional[LogType] = LogType.stdout
):
    """Command-line interface for the s3-downloader module."""
    assert bucket, "Bucket name is required."
    if workers:
        assert workers.isdigit(), "Workers must be a positive integer."
        workers = int(workers)
        assert isinstance(workers, int) and workers > 0, "Workers must be a positive integer."
    prefix_list = [p.strip() for p in prefix.split(",")] if prefix else None
    downloader = Downloader(bucket_name=bucket, download_dir=destination, prefix=prefix_list, log_type=LogType(log))
    entrypoint = f"Entrypoint: s3 {' '.join(sys.argv[1:])}"
    downloader.logger.info(entrypoint)
    click.secho(entrypoint, fg='green')
    if workers:
        downloader.run_in_parallel(threads=workers)
    else:
        downloader.run()
