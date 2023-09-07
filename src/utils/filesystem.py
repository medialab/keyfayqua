import gzip
from contextlib import contextmanager
from pathlib import PosixPath
import casanova
import os

import gzip
import shutil

from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)


@contextmanager
def open_infile(file):
    if isinstance(file, PosixPath):
        file = str(file)
    if file.endswith(".gz"):
        yield gzip.open(file, "rt")
    else:
        yield open(file, "r")


def compress_outfile(outfile):
    if isinstance(outfile, PosixPath):
        outfile = str(outfile)
    with open(outfile, "rb") as f_in:
        compressed_outfile = outfile + ".gz"
        print(f"\nCompressing output to '{compressed_outfile}'. Please wait.\n")
        try:
            with gzip.open(compressed_outfile, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            raise e
        else:
            os.remove(outfile)


def count_file_length(datafile) -> int:
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        SpinnerColumn(),
        TimeElapsedColumn(),
    ) as p:
        p.add_task(description="[bold]Measuring file length")
        infile_length = casanova.reader.count(datafile)
        return infile_length


class ParseEnricher:
    def __init__(self, infile, outfile, id_col) -> None:
        self.infile = infile
        self.outfile = outfile
        self.id_col = id_col

    def __enter__(self):
        self.open_outfile = open(self.outfile, "w")
        self.open_infile = open(self.infile, "r")
        # Try creating a Casanova enricher with a CSV file
        try:
            self.enricher = casanova.enricher(
                self.open_infile,
                self.open_outfile,
                select=[self.id_col],
                add=["parsed_text", "conll_string"],
            )
            self.enricher.headers
        # Try creating a Casanova enricher with a Gzip file
        except:
            self.open_infile = gzip.open(self.infile, "rt")
            self.enricher = casanova.enricher(
                self.open_infile,
                self.open_outfile,
                select=[self.id_col],
                add=["parsed_text", "conll_string"],
            )
        return self.enricher

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.open_infile:
            self.open_infile.close()
        if self.open_outfile:
            self.open_outfile.close()
