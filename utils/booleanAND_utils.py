import os


class InvalidPathError(Exception):
    pass


class ExistingFileError(Exception):
    pass


class MissingArgumentsError(Exception):
    pass


class IndexArtifactsNotFound(Exception):
    pass


INSTRUCTIONS = """
Please provide three positional arguments:\n1. The absolute path to the index directory.\n2. The absolute path to the JSON file containing topicID: Topic entries. (see README.md)\n3. The desired, absolute path for the text file containing the run details and results.
"""


def validate_input(index_directory_path, query_file_path, output_file_path):
    args = [
        arg for arg in [index_directory_path, query_file_path, output_file_path] if arg
    ]
    try:
        if len(args) < 3:
            raise MissingArgumentsError(
                f"Please enter index directory path, query file path, output file path.\n\nExpected: 3\nFound: {len(args)}"
            )
    except MissingArgumentsError as e:
        print(f"Missing Arguements Error. {e}\n{INSTRUCTIONS}")
        exit()


def validate_absolute_nature(index_directory_path, query_file_path, output_file_path):
    try:
        if not os.path.isabs(index_directory_path):
            raise InvalidPathError(
                "Please provide the absolute file path for the index directory path."
            )
        if not os.path.isabs(query_file_path):
            raise InvalidPathError(
                "Please provide the absolute file path for the query file path."
            )
        if not os.path.isabs(output_file_path):
            raise InvalidPathError(
                "Please provide the absolute file path for the output file path."
            )
    except InvalidPathError as e:
        print(f"Path Specification Error: {e}\n{INSTRUCTIONS}")
        exit()


def validate_existing_file(output_file_path):
    try:
        if os.path.exists(output_file_path):
            raise ExistingFileError(f"The destination result file path already exists.")
    except ExistingFileError as e:
        print(f"Existing File Error: {e}\n")
        exit()


def validate_index_artifacts(index_directory_path):
    try:
        mandatory_files = ["lexicon.txt", "index_registrar.txt", "inverted_index.json"]
        for file in mandatory_files:
            file_path = os.path.join(index_directory_path, file)
            if not os.path.exists(file_path):
                raise IndexArtifactsNotFound(
                    f"The file '{file}' does not exist in the directory '{index_directory_path}'"
                )
    except IndexArtifactsNotFound as e:
        print(f"Missing Index File: {e}\n")
        exit()


def validate_paths(index_directory_path, query_file_path, output_file_path):
    validate_input(index_directory_path, query_file_path, output_file_path)
    validate_absolute_nature(index_directory_path, query_file_path, output_file_path)
    validate_existing_file(output_file_path)
    validate_index_artifacts(index_directory_path)
