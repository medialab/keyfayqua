import subprocess
from enum import Enum
from pathlib import Path

import casanova
import click
import typer
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TotalFileSizeColumn,
)
from typing_extensions import Annotated

print("Importing NLP libraries...")
from src.normalizer import normalizer
from src.parsers import EnglishParser, FrenchParser
from src.utils import compress_outfile, open_infile

supported_languages = ["french", "english"]
DEFAULT_HOPSPARSER_MODEL_URI = "https://zenodo.org/record/7703346/files/UD_all_spoken_French-flaubert.tar.xz?download=1"
DEFAULT_HOPSPARSER_MODEL_NAME = "UD_all_spoken_French-flaubert"


class SupportedLang(str, Enum):
    en = "en"
    fr = "fr"


app = typer.Typer()


@app.command()
def parse(
    datafile: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    outfile: Annotated[Path, typer.Option(help="Path to file with Conll results")],
    id_col: Annotated[str, typer.Option(help="ID column name")],
    text_col: Annotated[str, typer.Option(help="Text column name")],
    lang: Annotated[
        SupportedLang, typer.Option(case_sensitive=False)
    ] = SupportedLang.en,
    clean_social: Annotated[bool, typer.Option("--clean-social")] = False,
):
    # STEP ONE --------------------------
    # Set up the Parser
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

    # STEP TWO --------------------------
    # Count the length of the in-file
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        SpinnerColumn(),
        TotalFileSizeColumn(),
        TimeElapsedColumn(),
    ) as p:
        p.add_task(description="[bold]Measuring file length")
        infile_length = casanova.reader.count(datafile)

    # STEP THREE --------------------------
    # Parse the document's texts
    if clean_social:
        add_cols = ["cleaned_text", "conll_string"]
    else:
        add_cols = ["conll_string"]

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ) as p:
        task = p.add_task(description="[bold cyan]Parsing...", total=infile_length)
        try:
            with open_infile(file=datafile) as f, open(outfile, "w") as of:
                enricher = casanova.enricher(
                    f,
                    of,
                    select=[id_col, text_col],
                    add=add_cols,
                )
                for row, text in enricher.cells(text_col, with_rows=True):
                    addendum = []
                    if clean_social:
                        text = normalizer(text)
                        addendum.append(text)
                    doc = parser(text)
                    addendum.append(doc._.conll_str)
                    enricher.writerow(row, addendum)
                    p.advance(task_id=task)

        except KeyboardInterrupt:
            print("\nKeyboard interrupted the program.")
            compress_outfile(outfile)

        else:
            compress_outfile(outfile)


@app.command()
def bye(name: str):
    print(f"Bye {name}")
