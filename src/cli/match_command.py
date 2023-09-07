import json
from typing import Generator
from collections import OrderedDict

import casanova
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
from rich.console import Console
from rich.table import Table


def display_columns(new_cols: list):
    table = Table(title="Semgrex Matches")
    table.add_column("Column name")
    [table.add_row(col) for col in new_cols]
    console = Console()
    console.print(table)


def conll_converter(
    enricher: casanova.Enricher, conll_col: str, parser: ConLLParser
) -> Generator[tuple[list, Doc], None, None]:
    for row, conll_str in enricher.cells(conll_col, with_rows=True):
        # Convert CoNLL into SpaCy Doc -------
        doc = parser(conll_str)
        yield row, doc


class MatchIndex:
    def __init__(self, file) -> None:
        with open(file, "r") as f:
            self.matches: dict = json.load(f)

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
            cols.append("{}id".format(col_prefix))
            cols.append("{}lemma".format(col_prefix))
            cols.append("{}pos".format(col_prefix))
            cols.append("{}deprel".format(col_prefix))
            cols.append("{}entity".format(col_prefix))
            cols.append("{}noun_phrase".format(col_prefix))

        self.columns = cols

        self.row_dict = OrderedDict()
        [self.row_dict.update({k: None}) for k in self.columns]

    def patterns(self) -> Generator[tuple[str, list], None, None]:
        for pattern_name, pattern_nodes in self.matches.items():
            yield pattern_name, pattern_nodes


def match_dependencies(
    doc: Doc, parser: FrenchParser | EnglishParser, match_index: MatchIndex
) -> Generator[list, None, None]:
    # Deploy DependencyMatcher
    matches_in_doc = parser.matcher(doc)

    # Parse matches in the document
    for pattern_hash, token_ids in matches_in_doc:
        # Unhash name matched pattern
        pattern_name = parser.nlp.vocab.strings[pattern_hash]

        # Get a list of the pattern's nodes
        _, pattern = parser.matcher.get(pattern_hash)

        # For this match pattern, create a new dictionary
        # in which to store node data
        d = match_index.row_dict.copy()

        # Add all the match's nodes to a row
        for i in range(len(token_ids)):
            node_name = pattern[0][i]["RIGHT_ID"]
            node_token = doc[token_ids[i]]
            col_prefix = form_column_prefix(
                pattern_name=pattern_name, node_name=node_name
            )
            d.update(
                {
                    "{}id".format(col_prefix): node_token.i,
                    "{}id".format(col_prefix): node_token.i,
                    "{}lemma".format(col_prefix): node_token.lemma_,
                    "{}pos".format(col_prefix): node_token.pos_,
                    "{}deprel".format(col_prefix): node_token.dep_,
                    "{}entity".format(col_prefix): node_token.ent_type_,
                }
            )

        # "{}noun_phrase".format(col_prefix): node_token.,
        yield list(d.values())


def form_column_prefix(pattern_name: str, node_name: str):
    return "{}_{}_".format(pattern_name, node_name.upper())
