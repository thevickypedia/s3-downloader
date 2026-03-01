"""Module to store all the custom exceptions and formatters.

>>> S3Error

"""

from typing import Dict

from s3.squire import convert_to_folder_structure, size_converter


class S3Error(Exception):
    """Custom error for base exception to the s3-downloader module."""


class BucketNotFound(S3Error):
    """Custom error for bucket not found."""


class NoObjectFound(S3Error):
    """Custom error for no objects found."""


class InvalidPrefix(S3Error):
    """Custom exception for invalid prefix value."""

    def __init__(self, prefix: str, bucket_name: str, available: Dict[str, int]):
        """Initialize an instance of ``InvalidPrefix`` object inherited from ``S3Error``

        Args:
            prefix: Prefix to limit the objects.
            bucket_name: Name of the S3 bucket.
            available: Available objects in the s3.
        """
        self.prefix = prefix
        self.bucket_name = bucket_name
        self.available = available
        super().__init__(self.format_error_message())

    def format_error_message(self):
        """Returns the formatter error message as a string."""
        return (f"\n\n\t{self.prefix!r} was not found in {self.bucket_name}.\n\t"
                f"Available: {self.available}\n\n{convert_to_folder_structure(self.available)}")
