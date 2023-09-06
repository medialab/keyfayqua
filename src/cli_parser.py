import subprocess
from pathlib import Path

import casanova
import click
import typer
from ebbe import as_chunks
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from src.normalizer import normalizer
from src.parsers import EnglishParser, FrenchParser
from src.utils import open_infile

CHUNK_SIZE = 100
DEFAULT_HOPSPARSER_MODEL_URI = "https://zenodo.org/record/7703346/files/UD_all_spoken_French-flaubert.tar.xz?download=1"
DEFAULT_HOPSPARSER_MODEL_NAME = "UD_all_spoken_French-flaubert"


def setup_parser(lang: str) -> FrenchParser | EnglishParser:
    if lang == "fr":
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
                ["tar", "-xf", "hopsparser_archive.tar.xz", "-C", hopsparser_model_dir]
            )
            french_model = str(
                Path(hopsparser_model_dir).joinpath(DEFAULT_HOPSPARSER_MODEL_NAME)
            )
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


def single_enricher(
    text_col: str,
    id_col: str,
    infile: Path | str,
    outfile: Path | str,
    clean_social: bool,
    parser: FrenchParser | EnglishParser,
    p: Progress,
    task: TaskID,
):
    """
    Performance:
        2 processes:
            - 1000 docs, batch size 100, threads 1 = 7:56
            - 1000 docs, batch size 100, threads 1 = 7:56
    """
    add_cols = ["parsed_text", "conll_string"]
    with open_infile(file=infile) as f, open(outfile, "w") as of:
        enricher = casanova.enricher(
            f,
            of,
            select=[id_col, text_col],
            add=add_cols,
        )
        for row, text in enricher.cells(text_col, with_rows=True):
            if clean_social:
                text = normalizer(text)
            doc = parser.nlp(text)
            enricher.writerow(row, [doc.text, doc._.conll_str])
            p.advance(task_id=task)


def batch_enricher(
    text_col: str,
    id_col: str,
    infile: Path | str,
    outfile: Path | str,
    clean_social: bool,
    parser: FrenchParser | EnglishParser,
    p: Progress,
    task: TaskID,
):
    """
    Performance (mac):
        1 process:
            - 1000 docs, batch size 50, threads 3 = 07:17
            - 1000 docs, batch size 100, threads 1 = 07:23
        1 process (with thinc-apple-ops):
            - 1000 docs, batch size 100, threads 1 = 07:02
        2 processes:
            - 1000 docs, batch size 100, threads 1 = 8:00
            - 1000 docs, batch size 100, threads 1 = 7:53
        3 processes (with thinc-apple-ops):
            - 1000 docs, batch size 100, threads 2 = 10:45
            - 1000 docs, batch size 100, threads 2 = 10:50
            - 1000 docs, batch size 100, threads 2 = 10:57
    """
    add_cols = ["parsed_text", "conll_string"]

    from spacy.tokens import Doc

    Doc.set_extension("doc_id", default=None)
    Doc.set_extension("original_text", default=None)

    with open_infile(file=infile) as f, open(outfile, "w") as of:
        enricher = casanova.enricher(
            f,
            of,
            select=[id_col, text_col],
            add=add_cols,
        )
        for chunk in as_chunks(
            size=CHUNK_SIZE, iterable=enricher.cells(text_col, with_rows=True)
        ):
            # Reverse the tuples that casanova produces,
            # putting the text first and the row second
            reverse_tuples = [t[::-1] for t in chunk]

            # If necessary, clean the text
            if clean_social:
                reverse_tuples = [(normalizer(t[0]), t[1]) for t in reverse_tuples]

            # Whenever doc is done, write Conll string and row to file
            for doc, row in parser.nlp.pipe(reverse_tuples, as_tuples=True):
                enricher.writerow(
                    row,
                    [doc.text, doc._.conll_str],
                )
                p.advance(task_id=task)
