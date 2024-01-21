import click
import json
import re
from typing import List, Dict, Tuple
from utils.booleanAND_utils import validate_paths

Q0 = "QO"
RUNTAG = "ctiscareAND"


def load_json_file(file_path: str) -> Dict:
    with open(file_path) as file:
        return json.load(file)


def process_query_topics(query_topics: Dict) -> Dict[str, List[str]]:
    search_tokens = {}
    for key, value in query_topics.items():
        if int(key) in (416, 423, 437, 444, 447):
            continue
        cleaned_query = value.replace("\n", " ").replace("_", " ")
        query_tokens = re.sub(r"\W+", ", ", cleaned_query).lower().split(", ")
        search_tokens[key] = query_tokens
    return search_tokens


def load_lexicon(file_path: str) -> Dict[str, int]:
    with open(file_path) as file:
        lexicon = file.read().splitlines()
    return {word: index for index, word in enumerate(lexicon, 1)}


def load_index_registrar(file_path: str) -> Dict[int, str]:
    with open(file_path) as file:
        index_registrar = file.read().splitlines()
    return {index: value for index, value in enumerate(index_registrar)}


def search_inverted_index(
    search_tokens: Dict[str, List[str]],
    lexicon: Dict[str, int],
    inverted_index: Dict[str, List[int]],
    index_registrar: Dict[int, str],
) -> List[Dict]:
    results = []
    for key, tokens in search_tokens.items():
        valid_tokens = [token for token in tokens if token in lexicon]
        if not valid_tokens:
            continue

        term_ids = [lexicon[token] for token in valid_tokens]
        collections = [
            inverted_index.get(str(term_id), [])[::2] for term_id in term_ids
        ]

        common_docs = set(collections[0]).intersection(*collections[1:])
        results.extend(create_final_results(key, common_docs, index_registrar))
    return results


def create_final_results(
    topic_id: str, doc_ids: set, index_registrar: Dict[int, str]
) -> List[Dict]:
    return [
        {
            "topicID": topic_id,
            "Q0": Q0,
            "docno": index_registrar[doc_id],
            "rank": str(index + 1),
            "score": str(len(doc_ids) - index),
            "runtag": RUNTAG,
        }
        for index, doc_id in enumerate(doc_ids)
    ]


def write_results_to_file(output_file_path: str, final_results: List[Dict]):
    with open(output_file_path, "a") as file:
        for result in final_results:
            file.write(" ".join(result.values()) + "\n")


@click.command()
@click.argument("index_directory_path", nargs=1, required=False)
@click.argument("query_file_path", nargs=1, required=False)
@click.argument("output_file_path", nargs=1, required=False)
def main(index_directory_path: str, query_file_path: str, output_file_path: str):
    validate_paths(index_directory_path, query_file_path, output_file_path)

    query_topics = load_json_file(query_file_path)
    search_tokens = process_query_topics(query_topics)

    lexicon = load_lexicon(f"{index_directory_path}/lexicon.txt")
    index_registrar = load_index_registrar(
        f"{index_directory_path}/index_registrar.txt"
    )
    inverted_index = load_json_file(f"{index_directory_path}/inverted_index.json")

    final_results = search_inverted_index(
        search_tokens, lexicon, inverted_index, index_registrar
    )
    write_results_to_file(output_file_path, final_results)


if __name__ == "__main__":
    main()
