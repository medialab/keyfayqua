print("importing NLP models...")
import subprocess
from pathlib import Path
from typing import Generator, Iterable, Tuple

import spacy
import spacy_stanza
import stanza
import typer
from hopsparser import spacy_component
from spacy.matcher import DependencyMatcher
from spacy.tokens.doc import Doc
from spacy_conll import init_parser
from spacy_conll.parser import ConllParser as SpacyConllParse

from src.constants import (
    DEFAULT_HOPSPARSER_MODEL_NAME,
    DEFAULT_HOPSPARSER_MODEL_URI,
    ModelType,
)
from src.exceptions import SpacyDownloadException, StanzaDownloadException


def setup_parser(model_type: ModelType, lang: str, model_path: str):
    # List the models that are supported SpaCy parsers
    spacy_parsers = [ModelType.stanza, ModelType.hop, ModelType.spacy]

    # If the user's selected model requires a SpaCy parser,
    # return that parser with the right pipeline and language
    if model_type in spacy_parsers:
        # If using spacy-hopsparser, get the model path
        if model_type == "hopsparser":
            model_path = confirm_hopsparser_model_path(model_path)
        # Return an instance of the SpacyParser
        return SpacyParser(model_type, lang, model_path)

    # Otherwise, return the default parser, which is SpaCy English
    else:
        # Use default
        print(
            "The given model type isn't recognized among the currently supported model types."
        )
        use_default = typer.confirm(
            "\nDo you want to use SpaCy's English parser?", abort=True
        )
        if use_default:
            return SpacyParser(ModelType.spacy, "en")


def confirm_hopsparser_model_path(model_path: str):
    # If the user provided a model path in the command, use that
    if model_path != "":
        return model_path
    # Otherwise, ask them about the Hopsparser model they want to use
    else:
        need_to_download = typer.confirm(
            "\nDo you need to download the Hopsparser model for French?"
        )
        if not need_to_download:
            french_model_path = typer.prompt(
                text="\nWhere is the downloaded Hopsparser model?",
            )
            return french_model_path
        else:
            print(f"\nDownloading model from: '{DEFAULT_HOPSPARSER_MODEL_URI}'")
            subprocess.run(
                [
                    "curl",
                    "-o",
                    "hopsparser_archive.tar.xz",
                    DEFAULT_HOPSPARSER_MODEL_URI,
                ]
            )
            hopsparser_model_dir = "hopsparser_model"
            Path(hopsparser_model_dir).mkdir(exist_ok=True)
            print(f"\nUnpacking model in directory '{hopsparser_model_dir}'...")
            subprocess.run(
                [
                    "tar",
                    "-xf",
                    "hopsparser_archive.tar.xz",
                    "-C",
                    hopsparser_model_dir,
                ]
            )
            return str(
                Path(hopsparser_model_dir).joinpath(DEFAULT_HOPSPARSER_MODEL_NAME)
            )


class SpacyParser:
    def __init__(self, model_type: ModelType, lang: str, model_path: str = "") -> None:
        # Set up the SpaCy pipeline

        # Depending on the model/plug-in, setup the pipeline
        if model_type == "stanza":
            try:
                stanza.download(lang, processors="tokenize,pos,lemma,depparse,ner")
            except Exception as e:
                raise StanzaDownloadException(e, lang)
            self.nlp = spacy_stanza.load_pipeline(
                lang,
                processors="tokenize,pos,lemma,depparse,ner",
            )
        elif model_type == "hopsparser":
            try:
                self.nlp = spacy.load(lang)
            except OSError as e:
                raise SpacyDownloadException(e, lang)
            self.nlp.add_pipe(
                "hopsparser", "hopsparser", config={"model_path": model_path}
            )
        elif model_type == "spacy":
            try:
                self.nlp = spacy.load(lang)
            except OSError as e:
                raise SpacyDownloadException(e, lang)
        else:
            self.nlp = spacy.load("en")

        # Add the CoNLL formatter
        self.nlp.add_pipe("conll_formatter", last=True)

        # Attach the DependencyMater
        self.matcher = DependencyMatcher(self.nlp.vocab)

    def annotate(
        self, batch: Iterable[Tuple[str, list]], batch_size: int
    ) -> Generator[Tuple[list[str], str, str], None, None]:
        """
        Feed batches of tuples (text, CSV row) to a SpaCy pipeline and return 3
        components disentangled: the CSV row, the parsed text, the CoNLL string.
        """
        for doc, context in self.nlp.pipe(batch, as_tuples=True, batch_size=batch_size):
            yield context, doc.text, doc._.conll_str

    def add_semgrex(self, patterns: dict):
        self.patterns = patterns
        for pattern_name, pattern in patterns.items():
            self.matcher.add(pattern_name, [pattern])


class BaseUDPipeParser:
    def __init__(self) -> None:
        pass


class ConLLParser:
    def __init__(self, spacy_language: str) -> None:
        # Load language
        self.nlp = SpacyConllParse(init_parser(spacy_language, "spacy"))

    def __call__(self, text: str) -> Doc:
        return self.nlp.parse_conll_text_as_spacy(text=text)
