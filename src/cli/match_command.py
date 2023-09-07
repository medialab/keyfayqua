import logging
from pathlib import Path
from typing import Generator

import casanova
from ebbe import Timer
from spacy.tokens.doc import Doc

from src.parsers import ConLLParser

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
        try:
            doc = parser(conll_str)
        except Exception as e:
            logging.exception(row[0], e)
        else:
            yield row, doc
