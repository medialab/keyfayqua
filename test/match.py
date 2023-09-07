import unittest
from pathlib import Path
import casanova
from src.constants import SupportedLang


from src.cli.match_command import MatchIndex, conll_converter
from src.utils.filesystem import MatchEnricher
from src.parsers import ConLLParser
from spacy.tokens.doc import Doc
from src.main import match

test_dir = Path("test")
outdir = test_dir.joinpath("data")


FRENCH_KWARGS = {
    "matchfile": test_dir.joinpath("semgrex", "matches.json"),
    "datafile": outdir.joinpath("french", "french.conll.csv.gz"),
    "outfile": outdir.joinpath("french", "french.deps.csv"),
    "model_path": "./hopsparser_model/UD_all_spoken_French-flaubert",
    "lang": SupportedLang.fr,
}

ENGLISH_KWARGS = {
    "matchfile": test_dir.joinpath("semgrex", "matches.json"),
    "datafile": outdir.joinpath("english", "english.conll.csv.gz"),
    "outfile": outdir.joinpath("english", "english.deps.csv"),
    "model_path": "./hopsparser_model/UD_all_spoken_French-flaubert",
    "lang": SupportedLang.en,
}


class MatchCommand(unittest.TestCase):
    def test_french(self):
        match(**FRENCH_KWARGS)


if __name__ == "__main__":
    unittest.main()
