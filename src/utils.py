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
