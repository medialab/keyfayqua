from typing import Generator, Iterable, Tuple

from casanova import Enricher, Reader
from ebbe import as_chunks
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from src.utils.normalizer import normalizer


ParseProgress = Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    MofNCompleteColumn(),
    TaskProgressColumn(),
    TimeElapsedColumn(),
    TimeRemainingColumn(),
)


def yield_batches_of_texts(
    reader: Enricher | Reader, text_col: str, batch_size: int
) -> Generator[Iterable[Tuple[str, list[str]]], None, None]:
    """
    From a tuple (a CSV row and a selected column), yield batches
    of tuples but inverted so that the first item in each tuple
    is the selected column (str) and the second item is the row (list).
    """

    def reverse_tuples(
        batch: Iterable[Tuple[list[str], str]]
    ) -> Iterable[Tuple[str, list[str]]]:
        """
        For every tuple in the batch, reverse the order, putting
        the text column (string) first and the row (list) second.
        """
        return [(text, row) for row, text in batch]

    for batch in as_chunks(
        size=batch_size, iterable=reader.cells(text_col, with_rows=True)
    ):
        yield reverse_tuples(batch)


def preprocess(batch) -> Iterable[Tuple[str, list[str]]]:
    """
    For every tuple of text and CSV row in a batch, pre-process the
    text and return the batch of text-row tuples.
    """
    return [(normalizer(text), row) for text, row in batch]
