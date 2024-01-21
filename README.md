# BM25 Search Algorithm

#### Created for MSCI 541, Search Engines.

## Overview
This README provides a comprehensive guide to the programs developed for MSCI 541 assignments, ranging from HW1 to HW5. The primary focus is on `search.py`, which is the main search program in HW5. Additionally, key details about the `index_engine.py`, `evaluator.py`, and `booleanAND.py` programs are included.

## Prerequisites

### Python
- Ensure Python is installed. To verify, run `python --version` or `python3 --version`.

### Repository Setup
- Clone the GitHub repository: `git clone <HTTPS Code>`.
- Ensure you are inside the repository after cloning.

### Virtual Environment (Optional)
- Create a virtual environment: `python -m venv myenv`.
- Activate the environment: `source myenv/bin/activate` (MacOS/Linux) or `.\myenv\Scripts\activate` (Windows).

### Required Packages
- Install necessary libraries: `pip install -r requirements.txt`.

## Programs Description

### Index Engine (`index_engine.py`)
- Generates and stores document metadata from the LA Times Data file.
- Accepts the path of the source data file and the destination directory for metadata storage.
- Example command: `python index_engine.py <source path> <destination path> <Porter Stemming Boolean>`.
- The directory structure follows YYYY/MM/DD/\<DOCNO\>.txt.

### Evaluator (`evaluator.py`)
- Computes effectiveness measures (e.g., average precision, NDCG) for a results file.
- Requires the absolute path of the QRELS file and the results file.
- Example command: `python evaluator.py <qrels file path> <results file path>`.

### BooleanAND (`booleanAND.py`)
- Retrieves documents using the BooleanAND algorithm.
- Requires the path of the index directory, query topics file, and desired results file path.
- Example command: `python booleanAND.py <index path> <topics file path> <results file path>`.

### Search Program (`search.py`)
- Interactive program using the BM25 algorithm with customizable parameters for document retrieval.
- Requires the absolute path of the index directory.
- Users can input queries, view document content, or start a new search.
- Example command: `python search.py <index directory path>`.

## Data Usage Note
- The LA Times data used in these assignments is protected under a course license and not included in the repository. Please use the provided test collection for the running and testing of the search engine.
