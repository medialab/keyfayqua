from pathlib import Path

import torch
import typer
from rich import print
from typing_extensions import Annotated

from src.cli.match_command import (
    MatchIndex,
    MatchProgress,
    conll_converter,
    display_columns,
    match_dependencies,
)
from src.cli.parse_command import ParseProgress, preprocess, yield_batches_of_texts
from src.cli.test_conll import parse_conll_string
from src.constants import CHUNK_SIZE, ModelType
from src.parsers import ConLLParser, setup_parser
from src.utils.filesystem import (
    MatchEnricher,
    ParseEnricher,
    compress_outfile,
    count_file_length,
)

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
    model: Annotated[ModelType, typer.Option(case_sensitive=False)] = ModelType.spacy,
    lang: str = "en",
    model_path: str = "",
    clean_social: Annotated[bool, typer.Option("--clean-social")] = False,
    batch_size: int = CHUNK_SIZE,
):
    # STEP ONE --------------------------
    # Set up the Parser
    torch.set_num_threads(2)
    print("Setting up parser...")
    parser = setup_parser(model, lang, model_path)
    if parser:
        # STEP TWO --------------------------
        # Count the length of the in-file
        infile_length = count_file_length(datafile)

        # STEP THREE --------------------------
        # Parse the document's texts
        with ParseProgress as p:
            task = p.add_task(description="[bold cyan]Parsing...", total=infile_length)
            try:
                with ParseEnricher(datafile, outfile, id_col) as enricher:
                    for batch in yield_batches_of_texts(enricher, text_col, batch_size):
                        # If necessary, pre-process the texts in the batch
                        if clean_social:
                            batch = preprocess(batch)

                        # Write each text document's ID, parsed text, and CoNLL string
                        for row, parsed_text, conll_string in parser.annotate(
                            batch=batch, batch_size=batch_size
                        ):
                            enricher.writerow(
                                row,  # row contains only ID column
                                [
                                    parsed_text,
                                    conll_string,
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
    model: Annotated[ModelType, typer.Option(case_sensitive=False)] = ModelType.stanza,
    spacy_language: str = "en_core_web_lg",
    lang: str = "en",
    model_path: str = "",
):
    torch.set_num_threads(1)
    # STEP ONE --------------------------
    # Set up the parsers
    conll_parser = ConLLParser(spacy_language=spacy_language)
    dep_parser = setup_parser(model, lang, model_path)
    if dep_parser:
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
        with MatchProgress as p:
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


@app.command("test-conll")
def test_conll(
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
    conll_col: Annotated[
        str, typer.Option(help="CoNLL string column name")
    ] = "conll_string",
):
    parse_conll_string(datafile=datafile, conll_string_col=conll_col)


if __name__ == "__main__":
    app()
