import unittest
from pathlib import Path

from src.constants import SupportedLang
from src.main import match

test_dir = Path("test")
outdir = test_dir.joinpath("data")


ENGLISH_KWARGS = {
    "datafile": outdir.joinpath("english", "english.conll.csv.gz"),
    "matchfile": test_dir.joinpath("semgrex", "matches.json"),
    "outfile": outdir.joinpath("english", "english.deps.csv"),
    "id_col": "id",
    "lang": SupportedLang.en,
}

FRENCH_KWARGS = {
    "datafile": outdir.joinpath("french", "french.conll.csv.gz"),
    "matchfile": test_dir.joinpath("semgrex", "matches.json"),
    "outfile": outdir.joinpath("french", "french.deps.csv"),
    "id_col": "id",
    "lang": SupportedLang.fr,
}


class EnglishTest(unittest.TestCase):
    def test_english(self):
        match(**ENGLISH_KWARGS)


class FrenchTest(unittest.TestCase):
    def test_french(self):
        match(**FRENCH_KWARGS)


if __name__ == "__main__":
    unittest.main()
