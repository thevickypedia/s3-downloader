"""Module to store all the custom exceptions and formatters.

>>> S3Error

"""

from typing import Dict, Set


class S3Error(Exception):
    """Custom error for base exception to the s3-downloader module."""


class BucketNotFound(S3Error):
    """Custom error for bucket not found."""


class NoObjectFound(S3Error):
    """Custom error for no objects found."""


def convert_to_folder_structure(sequence: Set[str]) -> str:
    """Convert objects in a s3 buckets into a folder like representation.

    Args:
        sequence: Takes either a mutable or immutable sequence as an argument.

    Returns:
        str:
        String representation of the architecture.
    """
    folder_structure = {}
    for item in sequence:
        parts = item.split('/')
        current_level = folder_structure
        for part in parts:
            current_level = current_level.setdefault(part, {})

    def generate_folder_structure(structure: Dict[str, dict], indent: str = '') -> str:
        """Generates the folder like structure.

        Args:
            structure: Structure of folder objects as key-value pairs.
            indent: Required indentation for the ASCII.
        """
        result = ''
        for i, (key, value) in enumerate(structure.items()):
            if i == len(structure) - 1:
                result += indent + '└── ' + key + '\n'
                sub_indent = indent + '    '
            else:
                result += indent + '├── ' + key + '\n'
                sub_indent = indent + '│   '
            if value:
                result += generate_folder_structure(value, sub_indent)
        return result

    return generate_folder_structure(folder_structure)


class InvalidPrefix(S3Error):
    """Custom exception for invalid prefix value."""

    def __init__(self, prefix: str, bucket_name: str, available: Set[str]):
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
