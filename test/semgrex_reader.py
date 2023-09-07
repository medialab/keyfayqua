import unittest
from pathlib import Path
import casanova

from src.cli.match_command import MatchIndex, conll_converter
from src.utils.filesystem import MatchEnricher
from src.parsers import ConLLParser
from spacy.tokens.doc import Doc

test_dir = Path("test")
outdir = test_dir.joinpath("data")


FRENCH_KWARGS = {
    "infile": outdir.joinpath("french", "french.conll.csv.gz"),
    "outfile": outdir.joinpath("french", "french.deps.csv"),
    "id_col": "id",
    "add_cols": [],
}

ENGLISH_KWARGS = {
    "infile": outdir.joinpath("english", "english.conll.csv.gz"),
    "outfile": outdir.joinpath("english", "english.deps.csv"),
    "id_col": "id",
    "add_cols": [],
}


class SemgrexIndex(unittest.TestCase):
    def test_reader(self):
        # Parse the semgrex patterns
        semgrex_file = test_dir.joinpath("semgrex", "matches.json")
        semgrex = MatchIndex(file=semgrex_file)

        # Set up the enricher
        FRENCH_KWARGS.update({"add_cols": semgrex.columns()})
        with MatchEnricher(**FRENCH_KWARGS) as _:
            pass

        with casanova.reader(FRENCH_KWARGS["outfile"]) as reader:
            fieldnames = reader.fieldnames

        assert sorted(["id"] + semgrex.columns()) == sorted(fieldnames)  # type: ignore


class CoNLLReader(unittest.TestCase):
    def test_french(self):
        parser = ConLLParser(lang="fr")

        with MatchEnricher(**FRENCH_KWARGS) as enricher:
            for _, doc in conll_converter(
                enricher=enricher, conll_col="conll_string", parser=parser
            ):
                assert isinstance(doc, Doc)

    def test_english(self):
        parser = ConLLParser(lang="en")

        with MatchEnricher(**ENGLISH_KWARGS) as enricher:
            for _, doc in conll_converter(
                enricher=enricher, conll_col="conll_string", parser=parser
            ):
                assert isinstance(doc, Doc)


if __name__ == "__main__":
    unittest.main()
