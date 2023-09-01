import gzip
from contextlib import contextmanager

import casanova
import click
from lxml import etree
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from constants import NS, OUTDIR, fields
from pipelines import ConllPipe, EnglishTokenizer, FrenchTokenizer, nlp_parser
from utils import normalizer
from xml_parser import build_dependency_tree, xml_to_row


@contextmanager
def open_infile(file):
    if file.endswith(".gz"):
        yield gzip.open(file, "rt")
    else:
        yield open(file, "r")


MAX_FILES = 10


@click.command()
# Declare the required basics
@click.argument("datafile", required=True)
@click.option("--conll-string-col", required=False)
@click.option("--cleaning-social", is_flag=True, default=False)
@click.option("--target", required=False)
# Prompt the user to declare names of required columns
@click.option("--id-col", prompt="ID column name: ", required=True)
@click.option("--text-col", prompt="Text column name: ", required=True)
# Prompt the user to choose a supported language
@click.option("--lang", prompt=True, type=click.Choice(["en", "fr"]))
def main(datafile, conll_string_col, cleaning_social, lang, id_col, text_col, target):
    # Make out-file
    outdir = OUTDIR.joinpath(lang)
    outdir.mkdir(exist_ok=True, parents=True)
    xml_file_dir = outdir.joinpath("xml")
    xml_file_dir.mkdir(exist_ok=True)
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
        enricher = casanova.enricher(f, of, select=[id_col, text_col], add=fields)
        id_col_pos = enricher.headers[id_col]

        if conll_string_col:
            pipe = ConllPipe(lang)
            text_col = conll_string_col
        else:
            if lang == "fr":
                pipe = FrenchTokenizer()
            else:
                pipe = EnglishTokenizer()

        # Set up task for progress bar
        task = progress.add_task(
            description="[bold red]Processing file...", total=file_length
        )

        # Set up directory and numbers for monitoring batches
        total_files_processed, batch_files_processed, batch_number = 0, 0, 1
        outdir = xml_file_dir.joinpath("batch_1")
        outdir.mkdir(exist_ok=True)

        for row, text in enricher.cells(text_col, with_rows=True):
            # Get the document's ID for the XML out file
            doc_id = row[id_col_pos]

            # Update the numbers and directories for monitoring batches
            total_files_processed += 1
            batch_files_processed += 1
            if batch_files_processed > 10:
                batch_number += 1
                batch_files_processed = 0
                outdir = xml_file_dir.joinpath(f"batch_{batch_number}")
                outdir.mkdir(exist_ok=True)
            outfile = outdir.joinpath(f"{doc_id}.xml")

            # If necessary, clean away social-media characters from text
            if cleaning_social:
                text = normalizer(text)

            # Parse the dependencies and convert into XML tree
            root = nlp_parser(text=text, nlp=pipe)

            # Write the XML tree to a file
            et = etree.ElementTree(root)
            et.write(outfile, pretty_print=True)

            # In Python, parse subject-object-verb triples in XML tree
            root = build_dependency_tree(root)

            # Parse triples and write to CSV file
            for sov in root.findall(".//subject-object-verb", namespaces=NS):
                result = xml_to_row(sov, target=target)
                if result:
                    enricher.writerow(row, result)

            # Advance the progress bar
            progress.advance(task_id=task)

            if total_files_processed > 25:
                break


if __name__ == "__main__":
    main()
