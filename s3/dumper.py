import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, NoReturn

import boto3
from botocore.config import Config
from tqdm import tqdm

from .display import Echo
from .exceptions import BucketNotFound

echo = Echo()


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

    def __init__(self, bucket_name: str,
                 download_dir: str = None,
                 region_name: str = os.environ.get("AWS_DEFAULT_REGION"),
                 aws_access_key_id: str = os.environ.get("AWS_ACCESS_KEY_ID"),
                 aws_secret_access_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY")):
        """Initiates all the necessary args.

        Args:
            bucket_name: Name of the bucket.
            download_dir: Name of the download directory. Defaults to bucket name.
            region_name: Name of the AWS region.
            aws_access_key_id: AWS access key ID.
            aws_secret_access_key: AWS secret access key.
        """
        _account_id, _alias = boto3.resource(service_name="iam", aws_secret_access_key=aws_secret_access_key,
                                             aws_access_key_id=aws_access_key_id).CurrentUser().arn.split("/")
        self.s3 = boto3.resource(service_name="s3", config=self.RETRY_CONFIG, region_name=region_name,
                                 aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        for bucket_ in self.s3.buckets.all():
            if bucket_.name == bucket_name:
                break
        else:
            raise BucketNotFound(
                f"{bucket_name} was not found in {_alias} account."
            )
        self.download_dir = download_dir or bucket_name
        echo.info(msg=f"Bucket objects from {bucket_name} will be dumped at {os.path.abspath(self.download_dir)}")
        self.bucket = self.s3.Bucket(bucket_name)
        self.bucket_name = bucket_name

    def _get_objects(self) -> List[str]:
        """Get all the objects in the target s3 bucket.

        Returns:
            list:
            List of objects.
        """
        if not os.path.isdir(self.download_dir):
            os.makedirs(name=self.download_dir)
            echo.info(msg=f"Created {os.path.abspath(path=self.download_dir)}")
        objects = [obj.key for obj in self.bucket.objects.all()]
        echo.info(f"Nuber of objects found in {self.bucket_name}: {len(objects)}")
        return objects

    def downloader(self, file: str) -> NoReturn:
        """Download the files in the exact path replacing spaces with underscores for the directory names.

        Args:
            file: Takes the filename as an argument.
        """
        path, filename = os.path.split(file)
        target_path = os.path.join(self.download_dir, path.replace(" ", "_"))
        if not os.path.isdir(target_path):
            os.makedirs(target_path)
        self.bucket.download_file(file, os.path.join(target_path, filename))

    def run(self) -> NoReturn:
        """Initiates bucket download in a traditional loop."""
        keys = self._get_objects()
        echo.info(msg="Initiating download process.")
        for file in tqdm(keys, total=len(keys), unit="file", leave=True,
                         desc=f"Downloading files from {self.bucket_name}"):
            self.downloader(file=file)

    def run_in_parallel(self, threads: int = 5) -> NoReturn:
        """Initiates bucket download in multi-threading.

        Args:
            threads: Number of threads to use for downloading using multi-threading.
        """
        echo.info(msg=f"Number of threads: {threads}")
        keys = self._get_objects()
        echo.info(msg="Initiating download process.")
        with ThreadPoolExecutor(max_workers=threads) as executor:
            list(tqdm(iterable=executor.map(self.downloader, keys),
                      total=len(keys), desc=f"Downloading files from {self.bucket_name}",
                      unit="files", leave=True))
        echo.info(f"Run Time: {round(float(time.perf_counter()), 2)}s")
