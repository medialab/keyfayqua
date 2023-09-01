from typing import Any

import spacy
import spacy_stanza
import stanza
from hopsparser import spacy_component
from lxml import etree
from spacy_conll import init_parser
from stanza.utils.conll import CoNLL
from spacy_conll.parser import ConllParser
import logging

logging.basicConfig(filename="nlp.log")

from constants import NS

HOPSPARSER_MODEL = "models/UD_French-FTB-flaubert"


class ConllPipe:
    def __init__(self, lang: str) -> None:
        if lang == "en":
            self.nlp = ConllParser(init_parser("en_core_web_sm", "spacy"))

    def __call__(self, text):
        return self.nlp.parse_conll_text_as_spacy(text)


class EnglishTokenizer:
    def __init__(self):
        stanza.download("en", processors="tokenize,pos,lemma,depparse")
        self.nlp = spacy_stanza.load_pipeline(
            "en", processors="tokenize,pos,lemma,depparse", threads=8
        )

    def __call__(self, text: str) -> Any:
        return self.nlp(text)


class FrenchTokenizer:
    def __init__(self) -> None:
        self.nlp = spacy.load("fr_core_news_sm")
        self.nlp.add_pipe(
            "hopsparser", "hopsparser", config={"model_path": HOPSPARSER_MODEL}
        )

    def __call__(self, text: str) -> Any:
        return self.nlp(text)


def nlp_parser(text, nlp: Any) -> etree._Element:
    # Create an XML tree root
    root = etree.Element("root", attrib={}, nsmap=NS)

    # Try parsing the document with the NLP pipeline
    try:
        doc = nlp(text)
    except Exception as e:
        logging.warning(e)

    # If successful, enrich the tree with nodes
    else:
        for sent in doc.sents:
            # For every sentence in the parsed document,
            # add a <sentence> node to the XML tree
            sentence = etree.SubElement(
                root,
                "sentence",
                attrib={
                    "start": str(sent.start_char),
                    "end": str(sent.end_char),
                    "text": sent.text,
                },
                nsmap=NS,
            )

            # Inside the sentence node, add a <tokens> node
            tokens = etree.SubElement(sentence, "tokens", nsmap=NS, attrib={})

            # For every token in the parsed document, parse the
            # relevant data and add a <token> node in <tokens>
            for token in sent:
                attrib = {
                    "id": str(token.idx),
                    "head_id": str(token.head.idx),
                    "dep": token.dep_,
                    "text": token.text,
                    "lemma": token.lemma_,
                    "tag": token.tag_,
                    "pos": token.pos_,
                }
                token_tag = etree.SubElement(tokens, "token", nsmap=NS, attrib=attrib)
                token_tag.text = attrib["text"]

    # Return the enriched root
    return root
