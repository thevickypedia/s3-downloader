import math
from collections.abc import Generator
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Union


def refine_prefix(prefix: Union[str, List[str]] = None) -> Generator[str]:
    """Refines the prefix input to ensure it is a list of strings.

    Args:
        prefix: A string or a list of strings representing the prefix(es) to filter S3 objects.

    Yields:
        str:
        Yields strings representing the refined prefix(es).
    """
    if isinstance(prefix, str):
        if prefix.endswith("/"):
            yield prefix
        yield f"{prefix}/"
    elif isinstance(prefix, list) and all(isinstance(p, str) for p in prefix):
        for p in prefix:
            if p.endswith("/"):
                yield p
            else:
                yield f"{p}/"
    else:
        raise ValueError("Prefix must be a string or a list of strings.")



def size_converter(byte_size: Union[int, float]) -> str:
    """Gets the current memory consumed and converts it to human friendly format.

    Args:
        byte_size: Receives byte size as argument.

    Returns:
        str:
        Converted human understandable size.
    """
    if byte_size == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    integer = int(math.floor(math.log(byte_size, 1024)))
    size = round(byte_size / pow(1024, integer), 2)
    return str(size) + ' ' + size_name[integer]


def convert_to_folder_structure(sequence: Dict[str, int]) -> str:
    """Convert objects in an S3 bucket into a folder-like representation including sizes.

    Args:
        sequence: A dictionary where keys are S3 object keys (paths) and values are their sizes in bytes.

    Returns:
        str:
        A string representing the folder structure of the S3 bucket, with each file and folder showing the size.
    """

    # Step 1: Build tree structure
    folder_structure = {}

    for path_, size_ in sequence.items():
        parts = path_.strip("/").split("/")
        current = folder_structure

        for part in parts[:-1]:
            current = current.setdefault(part, {})

        # Store file with size
        current.setdefault("__files__", []).append((parts[-1], size_))

    # Step 2: Recursive printer
    def generate_folder_structure(structure: Dict[str, dict], indent: str = "") -> (str, int):
        result = ""
        total_size = 0

        # Separate folders and files
        folders = [(k, v) for k, v in structure.items() if k != "__files__"]
        files = structure.get("__files__", [])

        entries = folders + [("__file__", f) for f in files]

        for i, (key, value) in enumerate(entries):
            is_last = i == len(entries) - 1

            branch = "└── " if is_last else "├── "
            sub_indent = indent + ("    " if is_last else "│   ")

            if key == "__file__":
                filename, size = value
                result += f"{indent}{branch}{filename} ({size_converter(size)})\n"
                total_size += size
            else:
                # Folder
                sub_result, sub_size = generate_folder_structure(value, sub_indent)
                result += f"{indent}{branch}{key} ({sub_size} bytes)\n"
                result += sub_result
                total_size += sub_size

        return result, total_size

    final_output_, total_size_ = generate_folder_structure(folder_structure)
    return f". ({size_converter(total_size_)})\n" + final_output_


def format_bucket_structure(bucket_structure: Dict[str, int], convert_size: bool) -> Dict[str, Any]:
    """Formats the bucket structure into a human-readable string.

    Args:
        bucket_structure: A dictionary where keys are S3 object keys (paths) and values are their sizes in bytes.
        convert_size: A boolean indicating whether to convert sizes to human-readable format.

    Returns:
        Dict[str, Any]:
        A dictionary representing the folder structure of the S3 bucket, with each file and folder showing the size.
    """
    tree = {}
    # Iterate over key + size
    for key, size in bucket_structure.items():
        parts = key.strip("/").split("/")
        current = tree

        for part in parts[:-1]:
            current = current.setdefault(part, {})

        # Add file with size
        current.setdefault("__files__", []).append({
            "name": parts[-1],
            "size": size
        })

    def clean(node: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively clean the tree structure and calculate folder sizes.

        Args:
            node: Each node in the tree structure.

        Returns:
            Dict[str, Any]:
            Cleaned node with separate "files" key for files and other keys for folders.
        """
        result = {}
        total_size = 0

        # Process files
        files = node.get("__files__", [])
        if files:
            result["files"] = sorted(files, key=lambda x: x["name"])
            total_size += sum(file_["size"] for file_ in files)

        # Process subfolders
        for k, v in node.items():
            if k == "__files__":
                continue
            cleaned_subfolder = clean(v)
            result[k] = cleaned_subfolder
            total_size += cleaned_subfolder.get("size", 0)

        # Add folder size
        result["size"] = total_size

        return result

    def size_it(node: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively convert sizes in the tree structure to human-readable format.

        Args:
            node: Each node in the tree structure.

        Returns:
            Dict[str, Any]:
            Node with sizes converted to human-readable format.
        """
        if "size" in node:
            node["size"] = size_converter(node["size"])
        for k, v in node.items():
            if isinstance(v, dict):
                size_it(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict) and "size" in item:
                        item["size"] = size_converter(item["size"])
        return node

    json_structure = clean(tree)
    return size_it(json_structure) if convert_size else json_structure



@dataclass
class S3Object:
    """Represents an S3 object with its key and size."""
    key: str
    size: int


class DownloadResults(dict):
    """Object to store results of S3 download.

    >>> DownloadResults

    """

    success: int = 0
    failed: int = 0
    skipped: int = 0


class Sort(Enum):
    """Enum to represent sorting options for S3 objects.

    >>> Sort

    """

    size: str = "size"
    size_desc: str = "size_desc"
    key: str = "key"
    key_desc: str = "key_desc"
    last_modified: str = "last_modified"
    last_modified_desc: str = "last_modified_desc"
    no_sort: str = "no_sort"
