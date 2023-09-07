from pathlib import Path

import torch
import typer
from ebbe import Timer
from rich import print
from typing_extensions import Annotated

from src.cli.match_command import (
    MatchIndex,
    MatchProgress,
    conll_converter,
    display_columns,
    match_dependencies,
)
from src.cli.parse_command import (
    ParseProgress,
    parser_batches,
    preprocess,
    setup_parser,
)
from src.constants import CHUNK_SIZE, SupportedLang
from src.parsers import ConLLParser
from src.utils.filesystem import (
    MatchEnricher,
    ParseEnricher,
    compress_outfile,
    count_file_length,
)

match_dir = Path("semgrex")
match_dir.mkdir(exist_ok=True)


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
    batch_size: int = CHUNK_SIZE,
    model_path: str | None = None,
):
    # STEP ONE --------------------------
    # Set up the Parser
    torch.set_num_threads(2)
    print("Setting up parser...")
    parser = setup_parser(lang, model_path)

    # STEP TWO --------------------------
    # Count the length of the in-file
    infile_length = count_file_length(datafile)

    # STEP THREE --------------------------
    # Parse the document's texts
    with ParseProgress as p, Timer(name="SpaCy pipeline"):
        task = p.add_task(description="[bold cyan]Parsing...", total=infile_length)
        try:
            with ParseEnricher(datafile, outfile, id_col) as enricher:
                for batch in parser_batches(enricher, text_col, batch_size):
                    # If necessary, pre-process the texts in the batch
                    if clean_social:
                        batch = preprocess(batch)

                    # Whenever text->SpaCy doc transformation is done,
                    # write the doc's ID, parsed text, and CoNLL string
                    for doc, row in parser.pipe(batch=batch, batch_size=batch_size):
                        enricher.writerow(
                            row,  # row contains only ID column
                            [
                                doc.text,
                                doc._.conll_str,
                            ],  # addendum contains parsed text and CoNLL string
                        )
                        # After parsing one doc, advance the progress bar forward
                        p.advance(task_id=task)

        except KeyboardInterrupt:
            print("\nKeyboard interrupted the program.")
            compress_outfile(outfile)

        else:
            compress_outfile(outfile)


@app.command()
def match(
    datafile: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="Path to file with Conll results",
        ),
    ],
    matchfile: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="Name of JSON file in semgrex folder",
        ),
    ],
    outfile: Annotated[Path, typer.Option(help="Path to file with dependency matches")],
    id_col: Annotated[str, typer.Option(help="ID column name")] = "id",
    conll_col: Annotated[
        str, typer.Option(help="CoNLL string column name")
    ] = "conll_string",
    lang: Annotated[
        SupportedLang, typer.Option(case_sensitive=False)
    ] = SupportedLang.en,
    model_path: str | None = None,
):
    torch.set_num_threads(1)
    # STEP ONE --------------------------
    # Set up the parsers
    conll_parser = ConLLParser(lang=lang)
    dep_parser = setup_parser(lang, model_path)

    # STEP TWO --------------------------
    # Parse the Semgrex patterns
    semgrex = MatchIndex(file=matchfile)
    dep_parser.add_semgrex(semgrex.matches)
    new_cols = list(semgrex.row_dict.keys())
    display_columns(new_cols)

    # STEP THREE --------------------------
    # Count the length of the in-file
    infile_length = count_file_length(datafile)

    # STEP FOUR --------------------------
    # Process the file
    with MatchProgress as p, Timer(name="DependencyMatcher"):
        task = p.add_task(description="[bold cyan]Matching...", total=infile_length)
        try:
            with MatchEnricher(
                infile=datafile, outfile=outfile, id_col=id_col, add_cols=new_cols
            ) as enricher:
                for row, doc in conll_converter(enricher, conll_col, conll_parser):
                    for matches in match_dependencies(
                        doc=doc, parser=dep_parser, match_index=semgrex
                    ):
                        enricher.writerow(row, matches)
                    p.advance(task)

        except KeyboardInterrupt:
            print("\nKeyboard interrupted the program.")
            compress_outfile(outfile)

        else:
            compress_outfile(outfile)
