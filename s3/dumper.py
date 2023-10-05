import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, NoReturn

import boto3
from botocore.config import Config
from tqdm import tqdm

from s3.logger import LOGGER


class Downloader:
    """Initiates Downloader object to download an entire S3 bucket.

    >>> Downloader

    """

    RETRY_CONFIG = Config(
        retries={
            "max_attempts": 10,
            "mode": "standard"
        }
    )

    def __init__(self, bucket_name: str = None,
                 download_dir: str = None,
                 region_name: str = os.environ.get("AWS_DEFAULT_REGION"),
                 profile_name: str = os.environ.get("PROFILE_NAME"),
                 aws_access_key_id: str = os.environ.get("AWS_ACCESS_KEY_ID"),
                 aws_secret_access_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY"),
                 logger: logging.Logger = LOGGER):
        """Initiates all the necessary args.

        Args:
            bucket_name: Name of the bucket.
            download_dir: Name of the download directory. Defaults to bucket name.
            region_name: Name of the AWS region.
            profile_name: AWS profile name.
            aws_access_key_id: AWS access key ID.
            aws_secret_access_key: AWS secret access key.
            logger: Bring your own logger.
        """
        self.session = boto3.Session(profile_name=profile_name,
                                     region_name=region_name,
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key)
        self.s3 = self.session.resource(service_name="s3", config=self.RETRY_CONFIG)
        self.no_filename = []
        self.logger = logger
        self.download_dir = download_dir or bucket_name
        self.bucket_name = bucket_name
        self.buckets = [bucket_.name for bucket_ in self.s3.buckets.all()]
        self.bucket = None

    def init(self) -> None:
        """Instantiates the bucket instance.

        Raises:
            ValueError: If no bucket name was passed.
            NotADirectoryError: If bucket name was not found.
        """
        if not self.bucket_name:
            raise ValueError(
                f"\n\n\tCannot proceed without a bucket name.\n\tAvailable: {self.buckets}"
            )
        _account_id, _alias = self.session.resource(service_name="iam").CurrentUser().arn.split("/")
        if self.bucket_name not in self.buckets:
            raise NotADirectoryError(
                f"\n\n\t{self.bucket_name} was not found in {_alias} account.\n\tAvailable: {self.buckets}"
            )
        self.logger.info("Bucket objects from %s will be dumped at %s",
                         self.bucket_name, os.path.abspath(self.download_dir))
        self.bucket = self.s3.Bucket(self.bucket_name)

    def exit(self) -> None:
        """Logs if there were any failures."""
        if self.no_filename:
            self.logger.warning("%d file(s) failed to download since no filename was specified", len(self.no_filename))
            self.logger.warning(self.no_filename)
            self.logger.info("This can most likely be a system generated file, review and remove it in s3 if need be.")

    def _get_objects(self) -> List[str]:
        """Get all the objects in the target s3 bucket.

        Returns:
            list:
            List of objects.
        """
        if not os.path.isdir(self.download_dir):
            os.makedirs(name=self.download_dir)
            self.logger.info(f"Created {os.path.abspath(path=self.download_dir)}")
        objects = [obj.key for obj in self.bucket.objects.all()]
        self.logger.info(f"Nuber of objects found in {self.bucket_name}: {len(objects)}")
        return objects

    def _downloader(self, file: str) -> NoReturn:
        """Download the files in the exact path replacing spaces with underscores for the directory names.

        Args:
            file: Takes the filename as an argument.
        """
        path, filename = os.path.split(file)
        if not filename:
            self.no_filename.append(file)
            return
        target_path = os.path.join(self.download_dir, path.replace(" ", "_"))
        try:
            os.makedirs(target_path)
        except FileExistsError:  # Multiple threads running simultaneously can cause this
            pass
        self.bucket.download_file(file, os.path.join(target_path, filename))

    def run(self) -> NoReturn:
        """Initiates bucket download in a traditional loop."""
        self.init()
        keys = self._get_objects()
        self.logger.debug(keys)
        self.logger.info("Initiating download process.")
        for file in tqdm(keys, total=len(keys), unit="file", leave=True,
                         desc=f"Downloading files from {self.bucket_name}"):
            self._downloader(file=file)
        self.exit()

    def run_in_parallel(self, threads: int = 5) -> NoReturn:
        """Initiates bucket download in multi-threading.

        Args:
            threads: Number of threads to use for downloading using multi-threading.
        """
        self.init()
        self.logger.info(f"Number of threads: {threads}")
        keys = self._get_objects()
        self.logger.info("Initiating download process.")
        with ThreadPoolExecutor(max_workers=threads) as executor:
            list(tqdm(iterable=executor.map(self._downloader, keys),
                      total=len(keys), desc=f"Downloading files from {self.bucket_name}",
                      unit="files", leave=True))
        self.logger.info(f"Run Time: {round(float(time.perf_counter()), 2)}s")
        self.exit()
