import click
import re
import time
import json
import statistics
import math
import datetime
import warnings
from art import text2art
from typing import Dict, Tuple, List, Set
from utils.search_utils import validate_paths

warnings.filterwarnings("ignore")

RETRIEVED_RESULTS_LIMIT = 10
K1 = 1.2
B = 0.75
CLEAN_TAG_PATTERN = re.compile(r"<.*?>|</.*?>")
DELIMITERS = [".", "!", "?"]
WRONGFUL_SELECTION_MSG = "Invalid selection, please try again."


def load_index_data(
    index_directory_path: str,
) -> Tuple[Dict[str, int], Dict[int, str], Dict[str, List[int]], List[int], float, int]:
    with open(f"{index_directory_path}/lexicon.txt") as f:
        lexicon = {v: i for i, v in enumerate(f.read().splitlines(), 1)}

    with open(f"{index_directory_path}/index_registrar.txt") as f:
        index_registrar = {i: v for i, v in enumerate(f.read().splitlines())}

    with open(f"{index_directory_path}/inverted_index.json") as f:
        inverted_index = json.load(f)

    with open(f"{index_directory_path}/doc-lengths.txt") as f:
        doc_lengths = [int(length.strip()) for length in f.readlines()]

    average_doc_length = statistics.fmean(doc_lengths)
    num_docs = len(doc_lengths)

    return (
        lexicon,
        index_registrar,
        inverted_index,
        doc_lengths,
        average_doc_length,
        num_docs,
    )


def process_query(
    query: str,
    lexicon: Dict[str, int],
    inverted_index: Dict[str, List[int]],
    doc_lengths: List[int],
    average_doc_length: float,
    num_docs: int,
) -> Dict[int, float]:
    query_tokens = re.sub(r"\W+", ", ", query).lower().split(", ")
    termIDs = [lexicon[token] for token in query_tokens if token in lexicon]
    if not termIDs:
        return {}

    document_scores = calculate_document_scores(
        termIDs, inverted_index, doc_lengths, average_doc_length, num_docs
    )
    sorted_scores = sorted(
        document_scores.items(), key=lambda item: item[1], reverse=True
    )
    return dict(sorted_scores[:RETRIEVED_RESULTS_LIMIT])


def calculate_document_scores(
    termIDs: List[int],
    inverted_index: Dict[str, List[int]],
    doc_lengths: List[int],
    average_doc_length: float,
    num_docs: int,
) -> Dict[int, float]:
    document_scores = {}
    for termID in termIDs:
        postings_list = inverted_index[str(termID)]
        documents, frequencies = postings_list[::2], postings_list[1::2]
        doc_frequencies = dict(zip(documents, frequencies))
        docs_with_term = len(documents)

        for doc, freq in doc_frequencies.items():
            doc_length = doc_lengths[doc]
            K = K1 * ((1 - B) + B * (doc_length / average_doc_length))
            score = (freq / (freq + K)) * math.log(
                (num_docs - docs_with_term + 0.5) / (docs_with_term + 0.5)
            )
            document_scores[doc] = document_scores.get(doc, 0) + score

    return document_scores


def lookup_by_docno(source_directory: str, docno: str) -> str:
    match = re.search("LA([0-9]{6})-[0-9]{4}", docno)
    match = match.group(1)
    date_components = datetime.datetime.strptime(match, "%m%d%y")
    year, month, day = date_components.year, date_components.month, date_components.day

    search_directory = f"{source_directory}/{year}/{month}/{day}/{docno}.txt"
    with open(search_directory) as f:
        output = f.read()
    return output


def compute_sentence_score(
    sentences: List[str], top_n: int, query_tokens: List[str]
) -> List[str]:
    scores = {sentence: 0 for sentence in sentences}
    for i, sentence in enumerate(sentences):
        if i == 0:
            scores[sentence] += 2

        words = re.sub(r"\W+", ", ", sentence).lower()
        words = list(filter(None, words.split(", ")))

        for word in words:
            if word in query_tokens:
                scores[sentence] += 1

        for query_token in query_tokens:
            if query_token in words:
                scores[sentence] += 1

        for i in range(len(words) - 1):
            if words[i] in query_tokens and words[i + 1] in query_tokens:
                scores[sentence] += 1

    top_sentences = sorted(scores, key=scores.get, reverse=True)[:top_n]  # type: ignore
    return top_sentences


def get_graphic(text: str) -> str:
    text = re.findall(r"<GRAPHIC>.*</GRAPHIC>", text, re.DOTALL)
    text = text[0] if text else ""
    text = CLEAN_TAG_PATTERN.sub("", text).replace("\n", " ").replace("_", " ")
    text = re.sub(" +", " ", text).strip()
    if len(text) > 50:
        return f"{text[:50].strip()}..."
    else:
        return f"{text}..."


def display_results(
    document_scores: Dict[int, float],
    index_registrar: Dict[int, str],
    index_directory_path: str,
    query_tokens: List[str],
) -> List[Dict[str, str]]:
    retrieved_docs = []
    for rank, (doc_id, score) in enumerate(document_scores.items(), 1):
        docno = index_registrar[doc_id]
        document = lookup_by_docno(index_directory_path, docno)
        document_split = document.split("\n")

        date = document_split[2].split("date: ")[1].strip()
        headline = document_split[3].split("headline: ")[1].strip()

        whole_text = " \n".join(document_split[5:])
        text = re.findall(r"<TEXT>.*</TEXT>", whole_text, re.DOTALL)
        text = text[0] if text else ""
        text = CLEAN_TAG_PATTERN.sub("", text).replace("\n", " ").replace("_", " ")
        text = re.sub(" +", " ", text).strip()

        if not headline:
            headline = f"{text[:50].strip()}..." if text else get_graphic(whole_text)

        sentences = re.findall(r".*?[.!?]", text)
        sentences = [
            sentence.strip() for sentence in sentences if len(sentence.split(" ")) >= 5
        ]
        top_sentences = " ".join(compute_sentence_score(sentences, 3, query_tokens))

        document_metadata = dict(
            rank=rank,
            headline=headline,
            date=date,
            query_biased_snippet=top_sentences,
            docno=docno,
        )
        retrieved_docs.append(document_metadata)

    for result in retrieved_docs:
        print(f"{result['rank']}. {result['headline']} ({result['date']})")
        print(f"{result['query_biased_snippet']} ({result['docno']})")
        print("\n")
    return retrieved_docs


def handle_user_actions(
    retrieved_docs: List[Dict[str, str]], index_directory_path: str
) -> None:
    while True:
        next_action = (
            input(
                "Please enter:\n1. The numeric rank of a document to view the full document.\n"
                "2. 'N' to launch a new query.\n"
                "3. 'Q' to exit the search program.\n\n"
            )
            .lower()
            .strip()
        )

        if next_action == "q":
            break
        elif next_action == "n":
            return
        elif next_action.isdigit():
            next_action = int(next_action)
            if next_action > 0 and next_action <= len(retrieved_docs):
                result = retrieved_docs[next_action - 1]
                document = lookup_by_docno(index_directory_path, result["docno"])
                print(document)
            else:
                print(WRONGFUL_SELECTION_MSG)
        else:
            print(WRONGFUL_SELECTION_MSG)


@click.command()
@click.argument("index_directory_path", nargs=1, required=False)
def main(index_directory_path: str) -> None:
    validate_paths(index_directory_path)
    (
        lexicon,
        index_registrar,
        inverted_index,
        doc_lengths,
        average_doc_length,
        num_docs,
    ) = load_index_data(index_directory_path)

    print(text2art("BM25 Search Engine"))

    while True:
        query = input(
            "\nPlease enter a search query (or type 'exit' to quit):\n"
        ).strip()
        if query.lower() == "exit":
            break
        if not query:
            print("No results returned for an empty query.")
            continue

        start_time = time.time()
        document_scores = process_query(
            query, lexicon, inverted_index, doc_lengths, average_doc_length, num_docs
        )

        if not document_scores:
            print(f"No results found for query: {query}")
            continue

        query_tokens = re.sub(r"\W+", ", ", query).lower().split(", ")
        retrieved_docs = display_results(
            document_scores, index_registrar, index_directory_path, query_tokens
        )
        print(f"Retrieval took {time.time() - start_time:.2f} seconds.\n")

        handle_user_actions(retrieved_docs, index_directory_path)


if __name__ == "__main__":
    main()
