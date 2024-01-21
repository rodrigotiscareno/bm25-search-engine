import os
import re
from typing import Optional


class InvalidPathError(Exception):
    pass


class ExistingDirectoryError(Exception):
    pass


class MissingArgumentError(Exception):
    pass


class InvalidPorterStemArgumentError(Exception):
    pass


INSTRUCTIONS = """
Please provide three positional arguments:\n1. The absolute path to the source data file.\n2. The absolute path to the desired, destination directory for the index.\n3. If the tokenizer includes Porter Stemming (True/False)
"""
CLEAN_TAG_PATTERN = re.compile(r"<.*?>|<\/.*?>")


def regex_capture(regex_expression: str, string: str) -> str:
    match = re.search(regex_expression, string)
    return match.group(1) if match else ""


def extract_tag_text(raw_document: str, tag: str) -> str:
    text = re.findall(f"<{tag}>.*<\/{tag}>", raw_document, re.DOTALL)
    cleaned_text = CLEAN_TAG_PATTERN.sub("", text[0] if text else "")
    return " ".join(cleaned_text.split()).replace("_", " ")


def parse_directories(
    destination_directory: str, year: int, month: int, day: int
) -> str:
    path = f"{destination_directory}/{year}/{month}/{day}"
    os.makedirs(path, exist_ok=True)
    return path


def validate_arguments(
    source: Optional[str], destination: Optional[str], porter_stem: bool
) -> None:
    args = [arg for arg in [source, destination, porter_stem] if arg]
    try:
        if len(args) < 3:
            raise MissingArgumentError(
                f"Please enter additional arguements.\n\nExpected: 3\nFound: {len(args)}"
            )
    except MissingArgumentError as e:
        print(f"Missing Arguements Error. {e}\n{INSTRUCTIONS}")
        exit()


def validate_absolute_nature(source: str, destination: str) -> None:
    try:
        if not os.path.isabs(source):
            raise InvalidPathError(
                "Please provide the absolute file path for the source data."
            )
        if not os.path.isabs(destination):
            raise InvalidPathError(
                "Please provide the absolute file path for the destination data."
            )
    except InvalidPathError as e:
        print(f"Path Specification Error: {e}\n{INSTRUCTIONS}")
        exit()


def validate_existing_directory(destination: str) -> None:
    try:
        if os.path.isdir(destination):
            raise ExistingDirectoryError(
                f"The destination directory: {destination} already exists."
            )
    except ExistingDirectoryError as e:
        print(f"Existing Directory Error: {e}\n")
        exit()


def validate_porter_stem(porter_stem: str) -> None:
    porter_stem = porter_stem.lower()
    try:
        if porter_stem != "true" and porter_stem != "false":
            raise InvalidPorterStemArgumentError(
                f"Please enter a True or False value for the Porter Stem argument."
            )
    except InvalidPorterStemArgumentError as e:
        print(f"Invalid Porter Stem Argument Error: {e}\n")
        exit()


def validate_paths(source: str, destination: str, porter_stem: str) -> None:
    validate_arguments(source, destination, porter_stem)
    validate_absolute_nature(source, destination)
    validate_existing_directory(destination)
    validate_porter_stem(porter_stem)
