import subprocess
from pathlib import Path

import click
import typer
from casanova import Enricher
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

from src.constants import DEFAULT_HOPSPARSER_MODEL_NAME, DEFAULT_HOPSPARSER_MODEL_URI
from src.parsers import EnglishParser, FrenchParser
from src.utils.normalizer import normalizer


def setup_parser(
    lang: str, model_path: str | None = None
) -> FrenchParser | EnglishParser:
    if lang == "fr":
        if not model_path:
            need_to_download = typer.confirm(
                "\nDo you need to download the Hopsparser model for French?"
            )
            if not need_to_download:
                french_model_path = click.prompt(
                    text="\nWhere is the downloaded Hopsparser model?",
                    type=click.Path(exists=True),
                )
                french_model = str(french_model_path)
            else:
                print(f"\nDownloading model from: '{DEFAULT_HOPSPARSER_MODEL_URI}'")
                subprocess.run(
                    [
                        "curl",
                        "-o",
                        "hopsparser_archive.tar.xz",
                        DEFAULT_HOPSPARSER_MODEL_URI,
                    ]
                )
                hopsparser_model_dir = "hopsparser_model"
                Path(hopsparser_model_dir).mkdir(exist_ok=True)
                print(f"\nUnpacking model in directory '{hopsparser_model_dir}'...")
                subprocess.run(
                    [
                        "tar",
                        "-xf",
                        "hopsparser_archive.tar.xz",
                        "-C",
                        hopsparser_model_dir,
                    ]
                )
                french_model = str(
                    Path(hopsparser_model_dir).joinpath(DEFAULT_HOPSPARSER_MODEL_NAME)
                )
        else:
            french_model = model_path
        parser = FrenchParser(model_path=french_model)
    else:
        parser = EnglishParser()
    return parser


ParseProgress = Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    MofNCompleteColumn(),
    TaskProgressColumn(),
    TimeElapsedColumn(),
    TimeRemainingColumn(),
)


def parser_batches(enricher: Enricher, text_col: str, batch_size: int):
    def reverse_tuples(batch: list[tuple]):
        return [t[::-1] for t in batch]

    for batch in as_chunks(
        size=batch_size, iterable=enricher.cells(text_col, with_rows=True)
    ):
        yield reverse_tuples(batch)


def preprocess(batch):
    return [(normalizer(t[0]), t[1]) for t in batch]
