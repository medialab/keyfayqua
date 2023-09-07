import unittest
from pathlib import Path

from src.constants import SupportedLang
from src.main import parse

test_dir = Path("test")
outdir = test_dir.joinpath("data")


ENGLISH_KWARGS = {
    "outfile": outdir.joinpath("english", "english.conll.csv"),
    "id_col": "id",
    "text_col": "text",
    "lang": SupportedLang.en,
    "clean_social": True,
}


FRENCH_KWARGS = {
    "outfile": outdir.joinpath("french", "french.conll.csv"),
    "id_col": "id",
    "text_col": "text",
    "lang": SupportedLang.fr,
    "clean_social": True,
    "model_path": "./hopsparser_model/UD_all_spoken_French-flaubert",
}


class English(unittest.TestCase):
    def test_small(self):
        df = outdir.joinpath("english", "english.small.text.csv")
        ENGLISH_KWARGS.update({"datafile": df})
        ENGLISH_KWARGS.update({"batch_size": 5})
        parse(**ENGLISH_KWARGS)

    def test_large(self):
        df = outdir.joinpath("english", "english.large.text.csv")
        ENGLISH_KWARGS.update({"datafile": df})
        ENGLISH_KWARGS.update({"batch_size": 500})
        parse(**ENGLISH_KWARGS)


class French(unittest.TestCase):
    def test_small(self):
        df = outdir.joinpath("french", "french.small.text.csv")
        FRENCH_KWARGS.update({"datafile": df})
        FRENCH_KWARGS.update({"batch_size": 5})
        parse(**FRENCH_KWARGS)

    def test_large(self):
        df = outdir.joinpath("french", "french.large.text.csv")
        FRENCH_KWARGS.update({"datafile": df})
        FRENCH_KWARGS.update({"batch_size": 500})
        parse(**FRENCH_KWARGS)


if __name__ == "__main__":
    unittest.main()
