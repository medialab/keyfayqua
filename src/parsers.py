import spacy
import spacy_stanza
import stanza
from hopsparser import spacy_component
from spacy.matcher import DependencyMatcher
from spacy_conll import init_parser
from spacy_conll.parser import ConllParser as SpacyConllParse
from spacy.tokens.doc import Doc
import spacy


class EnglishParser:
    def __init__(self):
        # Load language model
        stanza.download("en", processors="tokenize,pos,lemma,depparse,ner")
        self.nlp = spacy_stanza.load_pipeline(
            "en",
            processors="tokenize,pos,lemma,depparse,ner",
        )
        self.nlp.add_pipe("conll_formatter", last=True)

        # Create dependency matcher
        self.matcher = DependencyMatcher(self.nlp.vocab)

    def pipe(self, batch: list[tuple], batch_size: int):
        yield from self.nlp.pipe(batch, as_tuples=True, batch_size=batch_size)


class FrenchParser:
    def __init__(self, model_path: str) -> None:
        # Load language model
        self.nlp = spacy.load("fr_core_news_lg")
        self.nlp.add_pipe("hopsparser", "hopsparser", config={"model_path": model_path})
        self.nlp.add_pipe("conll_formatter", last=True)

        # Create dependency matcher
        self.matcher = DependencyMatcher(self.nlp.vocab)

    def pipe(self, batch: list[tuple], batch_size: int):
        yield from self.nlp.pipe(batch, as_tuples=True, batch_size=batch_size)


class ConLLParser:
    def __init__(self, lang: str) -> None:
        # Load language
        if lang == "fr":
            self.nlp = SpacyConllParse(init_parser("fr_core_news_lg", "spacy"))
        else:
            self.nlp = SpacyConllParse(init_parser("en_core_web_lg", "spacy"))

    def __call__(self, text: str) -> Doc:
        return self.nlp.parse_conll_text_as_spacy(text=text)
