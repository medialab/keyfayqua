import unittest
from pathlib import Path
from src.constants import ModelType

from src.main import match

test_dir = Path("test")
outdir = test_dir.joinpath("data")


FRENCH_KWARGS = {
    "matchfile": test_dir.joinpath("semgrex", "matches.json"),
    "datafile": outdir.joinpath("french", "french.conll.csv.gz"),
    "outfile": outdir.joinpath("french", "french.deps.csv"),
    "model_path": "./hopsparser_model/UD_all_spoken_French-flaubert",
    "model": ModelType.hop,
    "lang": "fr",
}

ENGLISH_KWARGS = {
    "matchfile": test_dir.joinpath("semgrex", "matches.json"),
    "datafile": outdir.joinpath("english", "english.conll.csv.gz"),
    "outfile": outdir.joinpath("english", "english.deps.csv"),
    "model_path": "./hopsparser_model/UD_all_spoken_French-flaubert",
    "model": ModelType.stanza,
    "lang": "en",
}


class MatchCommand(unittest.TestCase):
    def test_french(self):
        match(**FRENCH_KWARGS)


if __name__ == "__main__":
    unittest.main()
