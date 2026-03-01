import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Union

import boto3
from alive_progress import alive_bar
from boto3.s3.transfer import TransferConfig
from botocore.config import Config

from s3.exceptions import BucketNotFound, InvalidPrefix, NoObjectFound
from s3.logger import LogType, default_logger
from s3.progress import ProgressPercentage
from s3.squire import (DownloadResults, S3Object, convert_to_folder_structure,
                       format_bucket_structure, refine_prefix, size_converter)


class Downloader:
    """Initiates Downloader object to download an entire S3 bucket.

    >>> Downloader

    """

    # noinspection PyTypeChecker
    RETRY_CONFIG: Config = Config(
        retries={
            "max_attempts": 10,
            "mode": "standard"
        },
        connect_timeout=60,
        read_timeout=90,
    )

    TRANSFER_CONFIG: TransferConfig = TransferConfig(
        max_concurrency=10,
        num_download_attempts=10,
        multipart_threshold=1024 * 8,  # 8MB
        multipart_chunksize=1024 * 8,  # 8MB
        use_threads=True
    )

    def __init__(self, bucket_name: str,
                 download_dir: str = None,
                 region_name: str = None,
                 profile_name: str = None,
                 aws_access_key_id: str = None,
                 aws_secret_access_key: str = None,
                 logger: logging.Logger = None,
                 log_type: LogType = LogType.stdout,
                 prefix: Union[str, List[str]] = None,
                 retry_config: Config = RETRY_CONFIG,
                 transfer_config: TransferConfig = TRANSFER_CONFIG):
        """Initiates all the necessary args and creates a boto3 session with retry logic.

        Args:
            bucket_name: Name of the bucket.
            download_dir: Name of the download directory. Defaults to bucket name.
            region_name: Name of the AWS region.
            profile_name: AWS profile name.
            aws_access_key_id: AWS access key ID.
            aws_secret_access_key: AWS secret access key.
            logger: Bring your own logger.
            log_type: Type of logging output. Defaults to stdout.
            prefix: Specific path [OR] list of paths from which the objects have to be downloaded.
            retry_config: Custom retry configuration for boto3 client. Defaults to RETRY_CONFIG.
            transfer_config: Custom transfer configuration for boto3 client. Defaults to TRANSFER_CONFIG.
        """
        self.session = boto3.Session(
            profile_name=profile_name or os.environ.get("PROFILE_NAME"),
            region_name=region_name or os.environ.get("AWS_DEFAULT_REGION"),
            aws_access_key_id=aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
        )
        self.s3 = self.session.resource(service_name="s3", config=retry_config)
        self.transfer_config = transfer_config
        self.no_filename = []
        self.logger = logger or default_logger(log_type)
        self.file_logger = log_type == LogType.file
        self.download_dir = download_dir or bucket_name
        self.bucket_name = bucket_name
        self.bucket = None
        self.prefix_list = list(refine_prefix(prefix)) if prefix else None
        self.start_time = time.time()
        self.results = DownloadResults()
        self.alive_bar_kwargs = dict(title="Progress", bar="smooth", spinner=None, enrich_print=False)

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
        self.start_time = time.time()

    def exit(self) -> None:
        """Logs if there were any failures."""
        if self.no_filename:
            self.logger.warning("%d file(s) failed to download since no filename was specified", len(self.no_filename))
            self.logger.warning(self.no_filename)
            self.logger.info("This can most likely be a system generated file, review and remove it in s3 if need be.")
        self.logger.info("Successful downloads: %d", self.results.success)
        self.logger.info("Failed downloads: %d", self.results.failed)
        self.logger.info("Skipped downloads [duplicates]: %d", self.results.skipped)
        self.logger.info(f"Run Time: {round(float(time.time() - self.start_time), 2)}s")

    def get_objects(self) -> List[S3Object]:
        """Get all the objects in the target s3 bucket.

        Raises:
            InvalidPrefix: If no objects with the given path exists.
            NoObjectFound: If the bucket is empty.

        Returns:
            List[S3Object]:
            List of objects in the bucket.
        """
        if self.prefix_list:
            objects = []
            for prefix in self.prefix_list:
                if prefixed_objects := [obj for obj in self.bucket.objects.filter(Prefix=prefix)]:
                    objects.extend(prefixed_objects)
                    self.logger.info(
                        f"Number of objects found in {self.bucket_name} limited to {prefix!r}: {len(objects)}"
                    )
                else:
                    raise InvalidPrefix(prefix, self.bucket_name)
        else:
            objects: List[S3Object] = [obj for obj in self.bucket.objects.all()]
            self.logger.info(f"Nuber of objects found in {self.bucket_name}: {len(objects)}")
        if objects:
            if not os.path.isdir(self.download_dir):
                os.makedirs(name=self.download_dir)
                self.logger.info(f"Created {os.path.abspath(path=self.download_dir)}")
            return objects
        raise NoObjectFound(
            f"\n\n\tNo objects found in {self.bucket_name}"
        )

    def downloader(self, s3_object: S3Object, callback: ProgressPercentage) -> None:
        """Download the files in the exact path as in the bucket.

        Args:
            s3_object: Takes the ``S3Object`` as an argument.
            callback: Takes the ``ProgressPercentage`` callback to track download progress.

        See Also:
            - Checks if the file already exists and is of the same size to avoid redundant downloads.
        """
        source_file = s3_object.key
        path, filename = os.path.split(source_file)
        if not filename:
            self.no_filename.append(source_file)
            return
        target_path = os.path.join(self.download_dir, path)
        try:
            os.makedirs(target_path)
        except FileExistsError:  # Multiple threads running simultaneously can cause this
            pass
        target_file = os.path.join(target_path, filename)
        if os.path.isfile(target_file) and os.path.getsize(target_file) == s3_object.size:
            if self.file_logger:
                self.logger.info(
                    "%s already exists and is of the same size [%s], skipping download.",
                    target_file, size_converter(s3_object.size)
                )
            self.results.skipped += 1
            return
        if self.file_logger:
            self.logger.info("Downloading %s [%s] to %s", filename, size_converter(s3_object.size), target_path)
        self.bucket.download_file(source_file, target_file, Config=self.transfer_config, Callback=callback)
        if self.file_logger:
            self.logger.info("Downloaded %s to %s", filename, target_path)

    def get_downloads(self) -> List[S3Object]:
        """Filters out the objects that are not files and cannot be downloaded.

        Returns:
            List[S3Object]:
            List of objects that can be downloaded.
        """
        # TODO: Add sorting options
        #  Sort objects by size
        # objects = [obj for obj in sorted(self.get_objects(), key=lambda x: x.size, reverse=True)]
        objects = self.get_objects()
        ignored, s3_objects = [], []
        for obj in objects:
            if obj.key.endswith("/"):
                ignored.append(obj)
            else:
                s3_objects.append(obj)
        self.logger.debug("Ignoring objects (as folders): %s", ignored)
        self.logger.info(
            "Initiating download process for %d files. Ignoring %d folders.",
            len(s3_objects), len(ignored)
        )
        return s3_objects

    def run(self) -> None:
        """Initiates bucket download in a traditional loop."""
        self.init()
        s3_objects = self.get_downloads()
        with alive_bar(len(s3_objects), **self.alive_bar_kwargs) as overall_bar:
            for s3_object in s3_objects:
                progress_callback = ProgressPercentage(
                    filename=s3_object.key, size=s3_object.size, bar=overall_bar
                )
                try:
                    self.downloader(s3_object=s3_object, callback=progress_callback)
                except Exception as error:
                    if self.file_logger:
                        self.logger.error("Error downloading %s: %s", s3_object.key, str(error))
                    self.results.failed += 1
                except KeyboardInterrupt:
                    self.logger.warning("Download interrupted by user. Exiting...")
                    break
                overall_bar()  # increment overall progress bar
        self.exit()

    def run_in_parallel(self, threads: int = 5) -> None:
        """Initiates bucket download in multi-threading.

        Args:
            threads: Number of threads to use for downloading using multi-threading.
        """
        self.init()
        self.logger.info(f"Number of threads: {threads}")
        s3_objects = self.get_downloads()
        with alive_bar(len(s3_objects), **self.alive_bar_kwargs) as overall_bar:
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = {}
                for s3_object in s3_objects:
                    progress_callback = ProgressPercentage(
                        filename=s3_object.key, size=s3_object.size, bar=overall_bar
                    )
                    future = executor.submit(self.downloader, s3_object=s3_object, callback=progress_callback)
                    futures[future] = s3_object
                for future in futures:
                    try:
                        future.result()
                        self.results.success += 1
                    except Exception as error:
                        s3_object = futures[future]
                        if self.file_logger:
                            self.logger.error("Error downloading %s: %s", s3_object.key, str(error))
                        self.results.failed += 1
                    except KeyboardInterrupt:
                        self.logger.warning("Download interrupted by user. Exiting...")
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    overall_bar()  # Increment overall bar after each upload finishes
        self.exit()

    def get_bucket_structure(self, raw: bool = False) -> Union[str, Dict[str, int]]:
        """Gets all the objects in an S3 bucket and forms it into a hierarchical folder like representation.

        Returns:
            Union[str, Dict[str, int]]:
            Returns a hierarchical folder like representation of the chosen bucket or the set of objects if raw is True.
        """
        self.init()
        # Using list and set will yield the same results but using set we can isolate directories from files
        structure = {obj.key: obj.size for obj in self.bucket.objects.all()}
        if raw:
            return structure
        return convert_to_folder_structure(structure)

    def save_bucket_structure(self, filename: str = "bucket_structure.json", convert_size: bool = False) -> None:
        """Saves the bucket structure in a JSON file.

        Args:
            filename: Name of the file to save the bucket structure in.
            convert_size: Whether to convert the size into human-readable format or not.
        """
        assert filename.endswith(".json"), "Filename must end with .json"
        bucket_structure = self.get_bucket_structure(raw=True)
        json_structure = format_bucket_structure(bucket_structure, convert_size=convert_size)
        with open(filename, "w") as file:
            json.dump(json_structure, file, indent=2)
        self.logger.info("%s created successfully.", filename)

    def print_bucket_structure(self) -> None:
        """Prints all the objects in an S3 bucket with a folder like representation."""
        print(self.get_bucket_structure())
