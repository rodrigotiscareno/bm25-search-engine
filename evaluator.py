import click
import math
from typing import Dict, List, Tuple
from utils.evaluator_utils import validate_paths, EXPECTED_TOPICS


class ResultsParseError(Exception):
    pass


def average_precision(
    relevancy_profiles: Dict[str, List[Dict[str, str]]],
    topic_arr: List[List[str]],
    topic: str,
) -> float:
    running_precision = 0
    n_precision = 0
    n_relevance = 0
    rel = count_relevant_docs(relevancy_profiles, topic)
    for i, result in enumerate(topic_arr, 1):
        relevance = is_relevant(relevancy_profiles, topic, result[2])
        running_precision += relevance
        n_precision = running_precision / i
        n_relevance += n_precision * relevance
    return n_relevance / rel


def precision_10(
    relevancy_profiles: Dict[str, List[Dict[str, str]]],
    topic_arr: List[List[str]],
    topic: str,
) -> float:
    running_precision = 0
    n_precision = 0
    idx = 0
    for i in range(1, 11):
        if idx <= len(topic_arr) - 1:
            relevance = is_relevant(relevancy_profiles, topic, topic_arr[idx][2])
            running_precision += relevance
        n_precision = running_precision / i
        idx += 1

    return n_precision


def ideal_ranking_score(
    relevancy_profiles: Dict[str, List[Dict[str, str]]], topic: str, n: int
) -> float:
    rel_docs = count_relevant_docs(relevancy_profiles, topic)
    running_score = 0
    for i in range(1, rel_docs + 1):
        running_score += 1 / math.log2(i + 1)
        if i == n:
            break
    return running_score


def normalized_discount_cumulative_gain_n(
    relevancy_profiles: Dict[str, List[Dict[str, str]]],
    topic_arr: List[List[str]],
    topic: str,
    n: int,
) -> float:
    running_dcg = 0
    topic_len = len(topic_arr)
    for i, result in enumerate(topic_arr, 1):
        numerator = is_relevant(relevancy_profiles, topic, result[2])
        denominator = math.log2(i + 1)
        running_dcg += numerator / denominator
        if i == n or i == topic_len:
            ideal_ranking_arr = ideal_ranking_score(relevancy_profiles, topic, n)
            ndcg = running_dcg / ideal_ranking_arr
            return ndcg


def count_relevant_docs(
    relevancy_profiles: Dict[str, List[Dict[str, str]]], topic: str
) -> int:
    count = 0
    for i in relevancy_profiles[str(topic)]:
        count += int(i["relevant"])
    return count


def is_relevant(
    relevancy_profiles: Dict[str, List[Dict[str, str]]], topic: str, docno: str
) -> int:
    rs = relevancy_profiles[str(topic)]
    try:
        return int(list(filter(lambda r: r["docno"] == docno, rs))[0]["relevant"])
    except IndexError as e:
        return 0


def validate_line(current_line: List[str]) -> None:
    if len(current_line) != 6:
        raise ResultsParseError(
            f"Bad run: Invalid results file format. Line length Error.\nFound: {len(current_line)}\nExpected: 6"
        )
    try:
        float(current_line[3])
    except ValueError as e:
        raise ResultsParseError(
            f"Bad run; Invalid results file format. Could not compute '{current_line[3]}' as rank"
        )
    try:
        float(current_line[4])
    except ValueError as e:
        raise ResultsParseError(
            f"Bad run; Invalid results file format. Could not compute '{current_line[4]}' as score"
        )


def load_relevancy_profiles(qrel: str) -> Dict[str, List[Dict[str, str]]]:
    relevancy_profiles = {}
    with open(qrel, "r") as qrel_file:
        lines = qrel_file.readlines()
        for line in lines:
            currentLine = line.split(" ")
            currentLine[-1] = currentLine[-1].strip()
            if relevancy_profiles.get(currentLine[0]) is None:
                relevancy_profiles[currentLine[0]] = [
                    dict(docno=currentLine[2], relevant=currentLine[3])
                ]
            else:
                relevancy_profiles[currentLine[0]].append(
                    dict(docno=currentLine[2], relevant=currentLine[3])
                )
    return relevancy_profiles


def load_result_profiles(results: str) -> List[List[str]]:
    result_profiles = []
    with open(results, "r") as results_file:
        lines = results_file.readlines()
        for line in lines:
            current_line = line.split(" ")
            validate_line(current_line)
            current_line[-1] = current_line[-1].strip()
            result_profiles.append(current_line)
    return result_profiles


@click.command()
@click.argument("qrel", nargs=1, required=False)
@click.argument("results", nargs=1, required=False)
def main(qrel: str, results: str) -> None:
    validate_paths(qrel, results)
    relevancy_profiles = load_relevancy_profiles(qrel)
    result_profiles = load_result_profiles(results)

    average_precision_results = {}
    precision_10_results = {}
    ndcg_10_results = {}
    ndcg_1000_results = {}
    current_topic_arr = []
    current_topic = None
    for line in result_profiles:
        if current_topic is None:
            current_topic = line[0]

        topic = line[0]
        if topic != current_topic:
            current_topic_arr = sorted(
                current_topic_arr, key=lambda x: (float(x[4]), x[2]), reverse=True
            )
            average_precision_results[current_topic] = average_precision(
                relevancy_profiles, current_topic_arr, current_topic
            )
            precision_10_results[current_topic] = precision_10(
                relevancy_profiles, current_topic_arr, current_topic
            )
            ndcg_10_results[current_topic] = normalized_discount_cumulative_gain_n(
                relevancy_profiles, current_topic_arr, current_topic, 10
            )
            ndcg_1000_results[current_topic] = normalized_discount_cumulative_gain_n(
                relevancy_profiles, current_topic_arr, current_topic, 1000
            )

            current_topic = topic
            current_topic_arr = []

        current_topic_arr.append(line)

    if current_topic_arr:
        average_precision_results[current_topic] = average_precision(
            relevancy_profiles, current_topic_arr, current_topic
        )
        precision_10_results[current_topic] = precision_10(
            relevancy_profiles, current_topic_arr, current_topic
        )
        ndcg_10_results[current_topic] = normalized_discount_cumulative_gain_n(
            relevancy_profiles, current_topic_arr, current_topic, 10
        )
        ndcg_1000_results[current_topic] = normalized_discount_cumulative_gain_n(
            relevancy_profiles, current_topic_arr, current_topic, 1000
        )

    for topic in EXPECTED_TOPICS:
        topic = str(topic)
        if topic not in average_precision_results.keys():
            average_precision_results[topic] = 0
        if topic not in precision_10_results.keys():
            precision_10_results[topic] = 0
        if topic not in ndcg_10_results.keys():
            ndcg_10_results[topic] = 0
        if topic not in ndcg_1000_results.keys():
            ndcg_1000_results[topic] = 0

    average_precision_metric = "{:.3f}".format(
        round(
            sum(average_precision_results.values())
            / len(average_precision_results.values()),
            3,
        )
    )
    precision_10_metric = "{:.3f}".format(
        round(
            sum(precision_10_results.values()) / len(precision_10_results.values()), 3
        )
    )
    ndcg_10_metric = "{:.3f}".format(
        round(sum(ndcg_10_results.values()) / len(ndcg_10_results.values()), 3)
    )
    ndcg_1000_metric = "{:.3f}".format(
        round(sum(ndcg_1000_results.values()) / len(ndcg_1000_results.values()), 3)
    )

    prefix = results.split("/")[-1].split(".")[0]

    with open(f"{prefix}_results.txt", "a") as results_file:
        average_precision_results = dict(sorted(average_precision_results.items()))
        precision_10_results = dict(sorted(precision_10_results.items()))
        ndcg_10_results = dict(sorted(ndcg_10_results.items()))
        ndcg_1000_results = dict(sorted(ndcg_1000_results.items()))
        for topic, ap in average_precision_results.items():
            results_file.write(f"ap {topic} {'{:.3f}'.format(round(ap,3))}\n")

        for topic, P_10 in precision_10_results.items():
            results_file.write(f"P_10 {topic} {'{:.3f}'.format(round(P_10,3))}\n")

        for topic, ndcg_cut_10 in ndcg_10_results.items():
            results_file.write(
                f"ndcg_cut_10 {topic} {'{:.3f}'.format(round(ndcg_cut_10,3))}\n"
            )

        for topic, ndcg_cut_1000 in ndcg_1000_results.items():
            results_file.write(
                f"ndcg_cut_1000 {topic} {'{:.3f}'.format(round(ndcg_cut_1000,3))}\n"
            )

        results_file.write(f"mean average precision: {average_precision_metric}\n")
        results_file.write(f"mean P@10: {precision_10_metric}\n")
        results_file.write(f"mean NDCG@10: {ndcg_10_metric}\n")
        results_file.write(f"mean NDCG@1000: {ndcg_1000_metric}\n")


if __name__ == "__main__":
    main()
