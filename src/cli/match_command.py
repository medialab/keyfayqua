from pathlib import Path

import casanova
from ebbe import Timer
from spacy.tokens.doc import Doc

from src.parsers import ConLLParser
from src.utils.filesystem import open_infile


def conll_parsing(parser: ConLLParser, datafile: Path):
    with open_infile(datafile) as f, Timer():
        reader = casanova.reader(f)
        for row, conllstr in reader.cells("conll_string", with_rows=True):
            print(conllstr)
            doc = parser(conllstr)
            assert isinstance(doc, Doc)
