from enum import Enum

CHUNK_SIZE = 5000
DEFAULT_HOPSPARSER_MODEL_URI = "https://zenodo.org/record/7703346/files/UD_all_spoken_French-flaubert.tar.xz?download=1"
DEFAULT_HOPSPARSER_MODEL_NAME = "UD_all_spoken_French-flaubert"


class SupportedLang(str, Enum):
    en = "en"
    fr = "fr"
