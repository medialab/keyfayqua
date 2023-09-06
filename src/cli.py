from enum import Enum
from pathlib import Path

import typer
from ebbe import Timer
from typing_extensions import Annotated

from src.cli_parser import ParseProgress, batch_enricher, setup_parser, single_enricher
from src.utils import compress_outfile, count_file_length

supported_languages = ["french", "english"]


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
    id_col: Annotated[str, typer.Option(help="ID column name")] = "id",
    text_col: Annotated[str, typer.Option(help="Text column name")] = "text",
    lang: Annotated[
        SupportedLang, typer.Option(case_sensitive=False)
    ] = SupportedLang.en,
    clean_social: Annotated[bool, typer.Option("--clean-social")] = False,
):
    # STEP ONE --------------------------
    # Set up the Parser
    import torch

    torch.set_num_threads(2)
    print("Setting up parser...")
    parser = setup_parser(lang)

    # STEP TWO --------------------------
    # Count the length of the in-file
    infile_length = count_file_length(datafile)

    # STEP THREE --------------------------
    # Parse the document's texts
    with ParseProgress as p, Timer(name="SpaCy pipeline"):
        task = p.add_task(description="[bold cyan]Parsing...", total=infile_length)
        try:
            batch_enricher(
                text_col=text_col,
                id_col=id_col,
                infile=datafile,
                outfile=outfile,
                clean_social=clean_social,
                parser=parser,
                p=p,
                task=task,
            )

        except KeyboardInterrupt:
            print("\nKeyboard interrupted the program.")
            compress_outfile(outfile)

        else:
            compress_outfile(outfile)


@app.command()
def bye(name: str):
    print(f"Bye {name}")
