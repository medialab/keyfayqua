from pathlib import Path

import casanova
from spacy.tokens.doc import Doc
from spacy_conll import init_parser
from spacy_conll.parser import ConllParser
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    MofNCompleteColumn,
)


def parse_conll_string(datafile: Path, conll_string_col: str):
    # Set up a ConLL parser.
    # For testing, the language doesn't matter
    print("Initializing parser...")
    nlp = ConllParser(init_parser("en_core_web_lg", "spacy"))

    print("Counting data file length...")
    with Progress(SpinnerColumn()):
        file_length = casanova.reader.count(datafile)

    # In the file, assert that every CoNLL string
    # can be converted to a SpaCy document
    with casanova.reader(datafile) as reader, Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
    ) as progress:
        task = progress.add_task(description="Test CoNLL string", total=file_length)
        for conllstr in reader.cells(conll_string_col):
            try:
                doc = nlp.parse_conll_text_as_spacy(conllstr)  # type: ignore
                assert isinstance(doc, Doc)
                progress.advance(task_id=task)
            except Exception as e:
                print("Invalid CoNLL string :\n", conllstr)
                raise e
