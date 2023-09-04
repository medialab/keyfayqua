import gzip
from contextlib import contextmanager

import casanova
import click
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from constants import HOPSPARSER_MODEL, OUTDIR, fields
from pipelines import EnglishMatcher, FrenchMatcher, dependency_matcher
from utils import normalizer


@contextmanager
def open_infile(file):
    if file.endswith(".gz"):
        yield gzip.open(file, "rt")
    else:
        yield open(file, "r")


@click.command()
# Declare the required basics
@click.argument("datafile", required=True)
@click.option("--cleaning-social", is_flag=True, default=False)
@click.option("--target", required=False)
# Prompt the user to declare names of required columns
@click.option("--id-col", prompt="ID column name: ", required=True)
@click.option("--text-col", prompt="Text column name: ", required=True)
# Prompt the user to choose a supported language
@click.option("--lang", prompt=True, type=click.Choice(["en", "fr"]))
def main(datafile, cleaning_social, target, lang, id_col, text_col):
    # Make out-file
    outdir = OUTDIR.joinpath(lang)
    outdir.mkdir(exist_ok=True, parents=True)
    outfile = str(outdir.joinpath("output.csv"))

    # Count in-file
    with Progress(
        TextColumn("[progress.description]{task.description}"), SpinnerColumn()
    ) as progress:
        progress.add_task(description="[bold yellow]Counting file length...")
        file_length = casanova.reader.count(datafile)

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ) as progress, open(outfile, "w") as of, open_infile(datafile) as f:
        # Set up the CSV enricher
        enricher = casanova.enricher(
            f, of, select=[id_col, text_col], add=["cleaned_text"] + fields
        )

        if lang == "fr":
            pipe = EnglishMatcher(target=target)
        else:
            pipe = FrenchMatcher(model_path=HOPSPARSER_MODEL, target=target)

        # Set up task for progress bar
        task = progress.add_task(
            description="[bold red]Processing file...", total=file_length
        )

        for row, text in enricher.cells(text_col, with_rows=True):
            # If necessary, clean away social-media characters from text
            if cleaning_social:
                cleaned_text = normalizer(text)
            else:
                cleaned_text = text

            # Parse the dependencies
            sov_triples = dependency_matcher(text=cleaned_text, nlp=pipe)

            # Parse triples and write to CSV file
            for match in sov_triples:
                if match.target is not None or match.verb_lemma is not None:
                    enricher.writerow(row, [cleaned_text] + match.as_csv_row())

            # Advance the progress bar
            progress.advance(task_id=task)


if __name__ == "__main__":
    main()
