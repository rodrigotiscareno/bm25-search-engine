import os
import re
from typing import Any

INSTRUCTIONS = """
Please provide three positional arguments:\n1. The absolute path to the source data directory.\n2. The look-up identifier (id or docno).\n3. The lookup value for the chosen identifier.
"""


class InvalidPathError(Exception):
    pass


class InvalidDirectoryError(Exception):
    pass


class MissingArgumentsError(Exception):
    pass


class InvalidIdentifierError(Exception):
    pass


class InvalidValueError(Exception):
    pass


def validate_input(source_directory: str, identifier: str, value: Any) -> None:
    args = [arg for arg in [source_directory, identifier, value] if arg]
    try:
        if len(args) < 3:
            raise MissingArgumentsError(
                f"Please enter source_directory, identifier, and value.\n\nExpected: 3\nFound: {len(args)}"
            )
    except MissingArgumentsError as e:
        print(f"Missing Arguements Error. {e}\n{INSTRUCTIONS}")
        exit()


def validate_absolute_nature(source_directory: str) -> None:
    try:
        if not os.path.isabs(source_directory):
            raise InvalidPathError(
                "Please provide the absolute file path for the source data."
            )
    except InvalidPathError as e:
        print(f"Path Specification Error: {e}\n{INSTRUCTIONS}")
        exit()


def validate_existing_directory(source_directory: str) -> None:
    try:
        if not os.path.isdir(source_directory):
            raise InvalidDirectoryError(
                f"The source directory: {source_directory} does not exist."
            )
    except InvalidDirectoryError as e:
        print(f"Invalid Directory Error: {e}")
        exit()


def validate_identifier_choice(identifier: str) -> None:
    try:
        if identifier not in ["id", "docno"]:
            raise InvalidIdentifierError(
                f"The identifier option: {identifier} does not exist. Please enter either id or docno."
            )
    except InvalidIdentifierError as e:
        print(f"Invalid Identifier Error: {e}")
        exit()


def enforce_value(identifier: str, value: str) -> None:
    try:
        if identifier == "docno" and not re.match(r"LA[0-9]{6}-[0-9]{4}", value):
            raise InvalidValueError(
                "Please enter a valid DOCNO value that follows the expected LA[0-9]{6}-[0-9]{4} format."
            )
    except InvalidValueError as e:
        print(f"Invalid Value Error: {e}")
        exit()

    try:
        if identifier == "id":
            try:
                int(value)
            except ValueError:
                raise InvalidValueError("Please enter a valid integer id value.")
    except InvalidValueError as e:
        print(f"Invalid Value Error: {e}")
        exit()


def validate_arguments(source_directory: str, identifier: str, value: str) -> None:
    validate_input(source_directory, identifier, value)
    validate_absolute_nature(source_directory)
    validate_existing_directory(source_directory)
    validate_identifier_choice(identifier)
    enforce_value(identifier, value)
