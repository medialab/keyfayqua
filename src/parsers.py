import logging
from datetime import datetime
from pathlib import Path
from typing import Any, List

import spacy
import spacy_stanza
import stanza
from hopsparser import spacy_component
from spacy.matcher import DependencyMatcher
from spacy_conll import init_parser


class EnglishParser:
    def __init__(self):
        # Load language model
        stanza.download("en", processors="tokenize,pos,lemma,depparse")
        self.nlp = spacy_stanza.load_pipeline(
            "en",
            processors="tokenize,pos,lemma,depparse",
        )
        self.nlp.add_pipe("conll_formatter", last=True)

        # Create dependency matcher
        self.matcher = DependencyMatcher(self.nlp.vocab)

    def __call__(self, text: str):
        return self.nlp(text)


class FrenchParser:
    def __init__(self, model_path: str) -> None:
        # Load language model
        self.nlp = spacy.load("fr_core_news_lg")
        self.nlp.add_pipe("hopsparser", "hopsparser", config={"model_path": model_path})
        self.nlp.add_pipe("conll_formatter", last=True)

        # Create dependency matcher
        self.matcher = DependencyMatcher(self.nlp.vocab)

    def __call__(self, text: str):
        return self.nlp(text)
