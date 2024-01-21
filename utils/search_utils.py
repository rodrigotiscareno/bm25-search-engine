import os

INSTRUCTIONS = """
Please provide one positional arguments:\n1. The absolute path to the index directory.
"""


class MissingArgumentsError(Exception):
    pass


class InvalidPathError(Exception):
    pass


class IndexArtifactsNotFound(Exception):
    pass


def validate_input(index_directory_path):
    args = [
        arg
        for arg in [
            index_directory_path,
        ]
        if arg
    ]
    try:
        if len(args) < 1:
            raise MissingArgumentsError(
                f"Please enter the absolute index directory path.\n\nExpected: 4\nFound: {len(args)}"
            )
    except MissingArgumentsError as e:
        print(f"Missing Arguements Error. {e}\n{INSTRUCTIONS}")
        exit()


def validate_absolute_nature(index_directory_path):
    try:
        if not os.path.isabs(index_directory_path):
            raise InvalidPathError(
                "Please provide the absolute file path for the index directory path."
            )
    except InvalidPathError as e:
        print(f"Path Specification Error: {e}\n{INSTRUCTIONS}")
        exit()


def validate_index_artifacts(index_directory_path):
    try:
        mandatory_files = [
            "lexicon.txt",
            "index_registrar.txt",
            "inverted_index.json",
            "doc-lengths.txt",
        ]
        for file in mandatory_files:
            file_path = os.path.join(index_directory_path, file)
            if not os.path.exists(file_path):
                raise IndexArtifactsNotFound(
                    f"The file '{file}' does not exist in the directory '{index_directory_path}'"
                )
    except IndexArtifactsNotFound as e:
        print(f"Missing Index File: {e}\n")
        exit()


def validate_paths(index_directory_path):
    validate_input(index_directory_path)
    validate_absolute_nature(index_directory_path)
    validate_index_artifacts(index_directory_path)
