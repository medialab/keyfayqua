import logging
from pathlib import Path
import json
from typing import Generator

import casanova
from ebbe import Timer
from spacy.tokens.doc import Doc

from src.parsers import ConLLParser, EnglishParser, FrenchParser

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

MatchProgress = Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    MofNCompleteColumn(),
    TaskProgressColumn(),
    TimeElapsedColumn(),
    TimeRemainingColumn(),
)


def conll_converter(
    enricher: casanova.Enricher, conll_col: str, parser: ConLLParser
) -> Generator[tuple[list, Doc], None, None]:
    for row, conll_str in enricher.cells(conll_col, with_rows=True):
        # Convert CoNLL into SpaCy Doc -------
        doc = parser(conll_str)
        yield row, doc


def match_dependencies(doc: Doc, parser: FrenchParser | EnglishParser):
    matches_in_doc = parser.matcher(doc)
    for pattern_hash, token_ids in matches_in_doc:
        pattern_name = parser.nlp.vocab.strings[pattern_hash]
        _, pattern = parser.matcher.get(pattern_hash)
        for i in range(len(token_ids)):
            node_name = pattern[0][i]["RIGHT_ID"]
            node_token = doc[token_ids[i]]
            col_suffix = form_column_prefix(
                pattern_name=pattern_name, node_name=node_name
            )


def form_column_prefix(pattern_name: str, node_name: str):
    return "{}-{}".format(pattern_name, node_name.upper())


class MatchIndex:
    def __init__(self, file) -> None:
        with open(file, "r") as f:
            self.matches: dict = json.load(f)

    def patterns(self) -> Generator[tuple[str, list], None, None]:
        for pattern_name, pattern_nodes in self.matches.items():
            yield pattern_name, pattern_nodes

    def columns(self):
        prefixes = []
        for pattern_name, pattern_nodes in self.patterns():
            for node in pattern_nodes:
                prefixes.append(
                    form_column_prefix(
                        pattern_name=pattern_name, node_name=node.get("RIGHT_ID")
                    )
                )

        cols = []
        for col_prefix in prefixes:
            cols.append("{}_id".format(col_prefix))
            cols.append("{}_lemma".format(col_prefix))
            cols.append("{}_pos".format(col_prefix))
            cols.append("{}_deprel".format(col_prefix))
            cols.append("{}_entity".format(col_prefix))
            cols.append("{}_noun_phrase".format(col_prefix))

        return cols
