import click
import datetime
import re
from typing import Optional

import get_doc_utils


def lookup_by_internal_id(source_directory: str, value: str) -> Optional[str]:
    index_registrar = f"{source_directory}/index_registrar.txt"
    with open(index_registrar, "r") as index_registrar:
        lines = index_registrar.readlines()
        index = int(value)
        try:
            docno = lines[index]
        except IndexError:
            return None
    docno = docno.strip()
    output = lookup_by_docno(source_directory, docno)
    return output


def lookup_by_docno(source_directory: str, docno: str) -> Optional[str]:
    match = re.search("LA([0-9]{6})-[0-9]{4}", docno)
    match = match.group(1)
    date_components = datetime.datetime.strptime(match, "%m%d%y")
    year, month, day = date_components.year, date_components.month, date_components.day

    search_directory = f"{source_directory}/{year}/{month}/{day}/{docno}.txt"
    with open(search_directory) as f:
        output = f.read()
    return output


@click.command()
@click.argument("source_directory", nargs=1, required=False)
@click.argument("identifier", nargs=1, required=False)
@click.argument("value", nargs=1, required=False)
def main(source_directory: str, identifier: str, value: str):
    get_doc_utils.validate_arguements(source_directory, identifier, value)
    identifier = identifier.lower()
    if identifier == "id":
        result = lookup_by_internal_id(source_directory, value)
    elif identifier == "docno":
        result = lookup_by_docno(source_directory, value)

    if result:
        print(result)
    else:
        print("Document Mismatch Error: Document not found.")


if __name__ == "__main__":
    main()
