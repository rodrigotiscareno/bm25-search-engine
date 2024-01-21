import click
import gzip
import re
import datetime
import os
import json
from nltk.stem import PorterStemmer
from typing import Tuple, List, Dict
from collections import Counter
from utils import index_engine_utils
import cProfile, pstats

ps = PorterStemmer()

DOCNO_REGEX = re.compile(r"<DOCNO>\s(.*)\s</DOCNO>")
DATE_REGEX = re.compile(r"LA([0-9]{6})-[0-9]{4}")


def tokenize(text: str, porter_stem: bool) -> List[str]:
    artifacts = re.sub(r"\W+", " ", text).lower()
    tokens = artifacts.split()
    return [ps.stem(token) if porter_stem else token for token in tokens]


def update_lexicon_and_inverted_index(
    tokenized: List[str],
    lexicon: Dict[str, int],
    inverted_index: Dict[int, List[int]],
    doc_id: int,
) -> None:
    term_counts = Counter(tokenized)
    for term, count in term_counts.items():
        if term not in lexicon:
            lexicon[term] = len(lexicon) + 1
        term_id = lexicon[term]
        if term_id not in inverted_index:
            inverted_index[term_id] = []
        inverted_index[term_id].extend([doc_id, count])


def register_document(doc_details: Dict[str, str], destination_directory: str) -> None:
    lines = [
        f"docno: {doc_details['docno']}\n",
        f"internal id: {doc_details['internal_id']}\n",
        f"date: {doc_details['date']}\n",
        f"headline: {doc_details['headline']}\n",
        f"raw document:\n{doc_details['raw_document']}",
    ]
    with open(f"{destination_directory}/{doc_details['docno']}.txt", "w") as f:
        f.writelines(lines)


def process_and_generate_document(
    document_features: List[str],
    destination_directory: str,
    doc_id: int,
    lexicon: Dict[str, int],
    inverted_index: Dict[int, List[int]],
    porter_stem: bool,
) -> Tuple[int, str]:
    raw_document = "\n".join(document_features)
    docno = index_engine_utils.regex_capture(DOCNO_REGEX, raw_document)
    date_component = datetime.datetime.strptime(
        index_engine_utils.regex_capture(DATE_REGEX, docno), "%m%d%y"
    )
    doc_details = {
        "docno": docno,
        "internal_id": doc_id,
        "date": date_component.strftime("%B %-d, %Y"),
        "headline": index_engine_utils.extract_tag_text(raw_document, "HEADLINE"),
        "text": index_engine_utils.extract_tag_text(raw_document, "TEXT"),
        "graphic": index_engine_utils.extract_tag_text(raw_document, "GRAPHIC"),
        "raw_document": raw_document,
    }

    path = index_engine_utils.parse_directories(
        destination_directory,
        date_component.year,
        date_component.month,
        date_component.day,
    )
    doc_details["destination_directory"] = path

    tokenized = tokenize(
        doc_details["graphic"]
        + " "
        + doc_details["text"]
        + " "
        + doc_details["headline"],
        porter_stem,
    )
    update_lexicon_and_inverted_index(tokenized, lexicon, inverted_index, doc_id)
    register_document(doc_details, path)

    return len(tokenized), docno


def process_file(
    source_file: str, destination_directory: str, porter_stem: bool
) -> None:
    raw_document, id, lexicon, inverted_index, doc_lengths = [], 0, {}, {}, []
    docnos = []
    os.mkdir(destination_directory)

    with gzip.open(source_file, "rt") as f:
        for line in f:
            line = line.strip()
            raw_document.append(line)
            if "</DOC>" in line:
                doc_length, docno = process_and_generate_document(
                    raw_document,
                    destination_directory,
                    id,
                    lexicon,
                    inverted_index,
                    porter_stem,
                )
                id += 1
                raw_document = []
                doc_lengths.append(doc_length)
                docnos.append(docno)

    with open(f"{destination_directory}/lexicon.txt", "a") as lexicon_registrar:
        for term, id in lexicon.items():
            lexicon_registrar.write(f"{term}\n")

    with open(
        f"{destination_directory}/inverted_index.json", "w"
    ) as inverted_index_registrar:
        json.dump(inverted_index, inverted_index_registrar)

    with open(f"{destination_directory}/doc-lengths.txt", "a") as doc_length_file:
        for length in doc_lengths:
            doc_length_file.write(f"{length}\n")

    with open(f"{destination_directory}/index_registrar.txt", "a") as index_file:
        for docno in docnos:
            index_file.write(f"{docno}\n")


@click.command()
@click.argument("source_file", nargs=1, required=False)
@click.argument("destination_directory", nargs=1, required=False)
@click.argument("porter_stem", nargs=1, required=False)
def main(source_file: str, destination_directory: str, porter_stem: str) -> None:
    profiler = cProfile.Profile()
    profiler.enable()
    index_engine_utils.validate_paths(source_file, destination_directory, porter_stem)
    porter_stem = True if porter_stem and porter_stem.lower() == "true" else False
    process_file(source_file, destination_directory, porter_stem)
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.print_stats()


if __name__ == "__main__":
    main()
