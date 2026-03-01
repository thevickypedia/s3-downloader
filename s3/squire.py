import math
from collections.abc import Generator
from typing import Dict, List, Union


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
