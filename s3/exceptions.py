class S3Error(Exception):
    """"""


class BucketNotFound(S3Error):
    """"""


def convert_to_folder_structure(input_set):
    folder_structure = {}
    for item in input_set:
        parts = item.split('/')
        current_level = folder_structure
        for part in parts:
            current_level = current_level.setdefault(part, {})

    def generate_folder_structure(structure, indent=''):
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


class InvalidDelimiter(S3Error):
    def __init__(self, delimiter, bucket_name, available):
        self.delimiter = delimiter
        self.bucket_name = bucket_name
        self.available = available
        super().__init__(self.format_error_message())

    def format_error_message(self):
        return (f"\n\n\t{self.delimiter!r} was not found in {self.bucket_name}.\n\t"
                f"Available: {self.available}\n\n{convert_to_folder_structure(self.available)}")
