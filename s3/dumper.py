import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, NoReturn

import boto3
from tqdm import tqdm

from .exceptions import BucketNotFound


class Downloader:
    """Initiates Downloader object to download all the objects in an S3 bucket.

    >>> Downloader

    """

    def __init__(self, bucket_name: str, download_dir: str = None, threads: int = 5,
                 region_name: str = None, aws_access_key_id: str = None, aws_secret_access_key: str = None):
        """Initiates all the necessary args.

        Args:
            bucket_name: Name of the bucket.
            download_dir: Name of the download directory. Defaults to bucket name.
            threads: Number of threads to use for downloading using multi-threading.
            region_name: Name of the AWS region.
            aws_access_key_id: AWS access key ID.
            aws_secret_access_key: AWS secret access key.
        """
        _account_id, _alias = boto3.resource('iam').CurrentUser().arn.split('/')
        self.s3 = boto3.resource('s3', region_name=region_name, aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key)
        for bucket_ in self.s3.buckets.all():
            if bucket_.name == bucket_name:
                break
        else:
            raise BucketNotFound(
                f"{bucket_name} was not found in {_alias} account."
            )
        self.bucket_name = bucket_name
        self.download_dir = download_dir or bucket_name
        self.bucket = self.s3.Bucket(self.bucket_name)
        self.threads = threads
        self.stop = False

    def get_objects(self) -> List[str]:
        """Get all the objects in the target s3 bucket.

        Returns:
            list:
            List of objects.
        """
        if not os.path.isdir(self.download_dir):
            os.makedirs(name=self.download_dir)
        return [obj.key for obj in self.bucket.objects.all()]

    def downloader(self, file: str) -> NoReturn:
        """Download the files in the exact path replacing spaces with underscores for the directory names.

        Args:
            file: Takes the filename as an argument.
        """
        if self.stop:
            return
        path, filename = os.path.split(file)
        target_path = self.download_dir + os.path.sep + path.replace(' ', '_')
        if not os.path.isdir(target_path):
            os.makedirs(target_path)
        self.bucket.download_file(file, f"{target_path}{os.path.sep}{filename}")

    def run(self) -> NoReturn:
        """Initiates bucket download in a traditional loop."""
        keys = self.get_objects()
        try:
            for k in tqdm(keys, total=len(keys), unit='file', leave=True,
                          desc=f'Downloading files from {self.bucket_name}'):
                self.downloader(file=k)
        except KeyboardInterrupt:
            self.stop = True

    def run_in_parallel(self) -> NoReturn:
        """Initiates bucket download in multi-threading."""
        keys = self.get_objects()
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            try:
                list(tqdm(iterable=executor.map(self.downloader, keys),
                          total=len(keys), desc=f'Downloading files from {self.bucket_name}',
                          unit='files', leave=True))
            except KeyboardInterrupt:
                self.stop = True
