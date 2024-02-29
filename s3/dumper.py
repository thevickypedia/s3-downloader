import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, NoReturn

import boto3
from botocore.config import Config
from tqdm import tqdm

from s3.exceptions import (BucketNotFound, InvalidPrefix, NoObjectFound,
                           convert_to_folder_structure)
from s3.logger import default_logger


class Downloader:
    """Initiates Downloader object to download an entire S3 bucket.

    >>> Downloader

    """

    RETRY_CONFIG: Config = Config(
        retries={
            "max_attempts": 10,
            "mode": "standard"
        }
    )

    def __init__(self, bucket_name: str,
                 download_dir: str = None,
                 region_name: str = None,
                 profile_name: str = None,
                 aws_access_key_id: str = None,
                 aws_secret_access_key: str = None,
                 logger: logging.Logger = None,
                 prefix: str = None):
        """Initiates all the necessary args and creates a boto3 session with retry logic.

        Args:
            bucket_name: Name of the bucket.
            download_dir: Name of the download directory. Defaults to bucket name.
            region_name: Name of the AWS region.
            profile_name: AWS profile name.
            aws_access_key_id: AWS access key ID.
            aws_secret_access_key: AWS secret access key.
            logger: Bring your own logger.
            prefix: Specific path from which the objects have to be downloaded.
        """
        self.session = boto3.Session(
            profile_name=profile_name or os.environ.get("PROFILE_NAME"),
            region_name=region_name or os.environ.get("AWS_DEFAULT_REGION"),
            aws_access_key_id=aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
        )
        self.s3 = self.session.resource(service_name="s3", config=self.RETRY_CONFIG)
        self.no_filename = []
        self.logger = logger or default_logger()
        self.download_dir = download_dir or bucket_name
        self.bucket_name = bucket_name
        self.bucket = None
        if prefix and prefix.endswith("/"):
            self.prefix = prefix
        elif prefix:
            self.prefix = f"{prefix}/"
        else:
            self.prefix = None

    def init(self) -> None:
        """Instantiates the bucket instance.

        Raises:
            ValueError: If no bucket name was passed.
            BucketNotFound: If bucket name was not found.
        """
        buckets = [bucket.name for bucket in self.s3.buckets.all()]
        if not self.bucket_name:
            raise ValueError(
                f"\n\n\tCannot proceed without a bucket name.\n\tAvailable: {buckets}"
            )
        _account_id, _alias = self.session.resource(service_name="iam").CurrentUser().arn.split("/")
        if self.bucket_name not in buckets:
            raise BucketNotFound(
                f"\n\n\t{self.bucket_name} was not found in {_alias} account.\n\tAvailable: {buckets}"
            )
        self.logger.info("Bucket objects from %s will be dumped at %s",
                         self.bucket_name, os.path.abspath(self.download_dir))
        self.bucket = self.s3.Bucket(self.bucket_name)

    def exit(self) -> NoReturn:
        """Logs if there were any failures."""
        if self.no_filename:
            self.logger.warning("%d file(s) failed to download since no filename was specified", len(self.no_filename))
            self.logger.warning(self.no_filename)
            self.logger.info("This can most likely be a system generated file, review and remove it in s3 if need be.")

    def get_objects(self) -> List[str]:
        """Get all the objects in the target s3 bucket.

        Raises:
            InvalidPrefix: If no objects with the given path exists.
            NoObjectFound: If the bucket is empty.

        Returns:
            list:
            List of objects in the bucket.
        """
        if self.prefix:
            objects = [obj.key for obj in self.bucket.objects.filter(Prefix=self.prefix)]
            if not objects:
                available = set()
                for obj in self.bucket.objects.all():
                    paths = obj.key.split('/')
                    if len(paths) > 1:  # folder like hierarchy
                        available.add('/'.join(paths[0:-1]))
                if available:  # this means hierarchical structure is present but just not with the same condition
                    raise InvalidPrefix(self.prefix, self.bucket_name, available)
            self.logger.info(
                f"Nuber of objects found in {self.bucket_name} limited to {self.prefix!r}: {len(objects)}"
            )
        else:
            objects = [obj.key for obj in self.bucket.objects.all()]
            self.logger.info(f"Nuber of objects found in {self.bucket_name}: {len(objects)}")
        if objects:
            if not os.path.isdir(self.download_dir):
                os.makedirs(name=self.download_dir)
                self.logger.info(f"Created {os.path.abspath(path=self.download_dir)}")
            return objects
        raise NoObjectFound(
            f"\n\n\tNo objects found in {self.bucket_name}"
        )

    def downloader(self, file: str) -> None:
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

    def run(self) -> None:
        """Initiates bucket download in a traditional loop."""
        self.init()
        keys = self.get_objects()
        self.logger.debug(keys)
        self.logger.info("Initiating download process.")
        for file in tqdm(keys, total=len(keys), unit="file", leave=True,
                         desc=f"Downloading files from {self.bucket_name}"):
            self.downloader(file=file)
        self.exit()

    def run_in_parallel(self, threads: int = 5) -> None:
        """Initiates bucket download in multi-threading.

        Args:
            threads: Number of threads to use for downloading using multi-threading.
        """
        self.init()
        self.logger.info(f"Number of threads: {threads}")
        keys = self.get_objects()
        self.logger.info("Initiating download process.")
        with ThreadPoolExecutor(max_workers=threads) as executor:
            list(tqdm(iterable=executor.map(self.downloader, keys),
                      total=len(keys), desc=f"Downloading files from {self.bucket_name}",
                      unit="files", leave=True))
        self.logger.info(f"Run Time: {round(float(time.perf_counter()), 2)}s")
        self.exit()

    def get_bucket_structure(self) -> str:
        """Gets all the objects in an S3 bucket and forms it into a hierarchical folder like representation.

        Returns:
            str:
            Returns a hierarchical folder like representation of the chosen bucket.
        """
        self.init()
        # Using list and set will yield the same results but using set we can isolate directories from files
        return convert_to_folder_structure(set([obj.key for obj in self.bucket.objects.all()]))

    def print_bucket_structure(self) -> None:
        """Prints all the objects in an S3 bucket with a folder like representation."""
        print(self.get_bucket_structure())
