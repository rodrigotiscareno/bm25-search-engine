import os


class InvalidPathError(Exception):
    pass


class FileDoesNotExistError(Exception):
    pass


class MissingArgumentsError(Exception):
    pass


class IndexArtifactsNotFound(Exception):
    pass


INSTRUCTIONS = """
Please provide three positional arguments:\n1. The absolute path to the QREL file.\n2. The absolute path to the individual results file, formatted in the standard TREC format.
"""


def validate_input(qrel, results):
    args = [arg for arg in [qrel, results] if arg]
    try:
        if len(args) < 2:
            raise MissingArgumentsError(
                f"Please enter QREL file path and the results file path.\n\nExpected: 2\nFound: {len(args)}"
            )
    except MissingArgumentsError as e:
        print(f"Missing Arguements Error. {e}\n{INSTRUCTIONS}")
        exit()


def validate_absolute_nature(qrel, results):
    try:
        if not os.path.isabs(qrel):
            raise InvalidPathError(
                "Please provide the absolute file path for the QREL file."
            )
        if not os.path.isabs(results):
            raise InvalidPathError(
                "Please provide the absolute file path for the results file."
            )
    except InvalidPathError as e:
        print(f"Path Specification Error: {e}\n{INSTRUCTIONS}")
        exit()


def validate_existing_file(qrel, results):
    try:
        if not os.path.exists(qrel):
            raise FileDoesNotExistError(
                f"The QRELS file does not exist according to the provided file path: {qrel}."
            )
    except FileDoesNotExistError as e:
        print(f"File Does Not Exist Error: {e}\n")
        exit()

    try:
        if not os.path.exists(results):
            raise FileDoesNotExistError(
                f"The results file does not exist according to the provided file path: {results}."
            )
    except FileDoesNotExistError as e:
        print(f"File Does Not Exist Error: {e}\n")
        exit()


def validate_paths(qrel, results):
    validate_input(qrel, results)
    validate_absolute_nature(qrel, results)
    validate_existing_file(qrel, results)


EXPECTED_TOPICS = [
    401,
    402,
    403,
    404,
    405,
    406,
    407,
    408,
    409,
    410,
    411,
    412,
    413,
    414,
    415,
    417,
    418,
    419,
    420,
    421,
    422,
    424,
    425,
    426,
    427,
    428,
    429,
    430,
    431,
    432,
    433,
    434,
    435,
    436,
    438,
    439,
    440,
    441,
    442,
    443,
    445,
    446,
    448,
    449,
    450,
]
