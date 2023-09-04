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

from constants import (
    ANCHOR_TARGET_PATTERN,
    ANCHOR_VERB_PATTERN,
    MODIFIER_PATTERN,
    NEGATION_PATTERN,
    OBJECT_PATTERN,
    SUBJECT_PATTERN,
    CSVRow,
)


def set_log_file(nlp: Any):
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    now = datetime.utcnow()
    time_str = "{}-{}-{}".format(now.hour, now.min, now.second)
    if isinstance(nlp, EnglishMatcher):
        logging.basicConfig(
            filename=output_dir.joinpath(f"english.{time_str}.log"), filemode="w"
        )
    elif isinstance(nlp, FrenchMatcher):
        logging.basicConfig(
            filename=output_dir.joinpath(f"french.{time_str}.log"), filemode="w"
        )


def build_sov_patterns(
    target: str | None = None, negation: bool = False
) -> List[List[dict]]:
    if not target:
        if not negation:
            return [
                [
                    ANCHOR_VERB_PATTERN,
                    SUBJECT_PATTERN,
                    OBJECT_PATTERN,
                ],
            ]
        else:
            return [
                [
                    ANCHOR_VERB_PATTERN,
                    SUBJECT_PATTERN,
                    OBJECT_PATTERN,
                    NEGATION_PATTERN,
                ],
            ]

    else:
        target_as_subject = SUBJECT_PATTERN.copy()
        target_as_subject["RIGHT_ATTRS"].update({"LOWER": target.lower()})
        target_as_object = OBJECT_PATTERN.copy()
        target_as_object["RIGHT_ATTRS"].update({"LOWER": target.lower()})
        if not negation:
            return [
                # Pattern with target as subject
                [
                    ANCHOR_VERB_PATTERN,
                    target_as_subject,
                    OBJECT_PATTERN,
                ],
                # Pattern with target as object
                [
                    ANCHOR_VERB_PATTERN,
                    SUBJECT_PATTERN,
                    target_as_object,
                ],
            ]
        else:
            return [
                # Pattern with target as subject
                [
                    ANCHOR_VERB_PATTERN,
                    target_as_subject,
                    OBJECT_PATTERN,
                    NEGATION_PATTERN,
                ],
                # Pattern with target as object
                [
                    ANCHOR_VERB_PATTERN,
                    SUBJECT_PATTERN,
                    target_as_object,
                    NEGATION_PATTERN,
                ],
            ]


def build_target_modifier_patterns(target: str) -> List[List[dict]]:
    anchor_pattern = ANCHOR_TARGET_PATTERN.copy()
    anchor_pattern["RIGHT_ATTRS"].update({"LOWER": target.lower()})
    return [
        [
            anchor_pattern,
            MODIFIER_PATTERN,
        ],
    ]


class EnglishMatcher:
    def __init__(self, target: str | None = None):
        # Load language model
        stanza.download("en", processors="tokenize,pos,lemma,depparse")
        self.nlp = spacy_stanza.load_pipeline(
            "en",
            processors="tokenize,pos,lemma,depparse",
        )
        self.nlp.add_pipe("conll_formatter", last=True)

        # Create dependency matcher
        self.matcher = DependencyMatcher(self.nlp.vocab)

        # Add Semgrex patterns to dependecy matcher
        self.sov_patterns = build_sov_patterns()
        self.matcher.add("SOV", self.sov_patterns)

        self.neg_sov_patterns = build_sov_patterns(negation=True)
        self.matcher.add("NEGSOV", self.neg_sov_patterns)

        if target:
            self.modifier_patterns = build_target_modifier_patterns(target)
            self.matcher.add("TM", self.modifier_patterns)

    def __call__(self, text: str):
        return self.nlp(text)


class FrenchMatcher:
    def __init__(self, model_path: str, target: str | None = None) -> None:
        # Load language model
        self.nlp = spacy.load("fr_core_news_lg")
        self.nlp.add_pipe("hopsparser", "hopsparser", config={"model_path": model_path})
        self.nlp.add_pipe("conll_formatter", last=True)

        # Create dependency matcher
        self.matcher = DependencyMatcher(self.nlp.vocab)

        # Add Semgrex patterns to depdendency matcher
        self.sov_patterns = build_sov_patterns()
        self.matcher.add("SOV", self.sov_patterns)

        self.neg_sov_patterns = build_sov_patterns(negation=True)
        self.matcher.add("NEGSOV", self.neg_sov_patterns)

        if target:
            self.modifier_patterns = build_target_modifier_patterns(target)
            self.matcher.add("TM", self.modifier_patterns)

    def __call__(self, text: str):
        return self.nlp(text)


def dependency_matcher(doc, nlp: Any) -> list:
    sov_triples = []
    for dep_match in nlp.matcher(doc):
        row = CSVRow()
        _, matches = dep_match[0], dep_match[1]

        # If matching on target-modifier pattern (2)
        if len(matches) == 2:
            target_token, modifier_token = doc[matches[0]], doc[matches[1]]

            row = CSVRow(
                **{
                    "target": target_token.lemma_,
                    "target_id": target_token.i,
                    "target_modifier": modifier_token.lemma_,
                    "target_modifier_pos": modifier_token.pos_,
                    "target_modifier_deprel": modifier_token.dep_,
                    "target_modifier_id": modifier_token.i,
                }
            )

        # If matching on subject-object-verb (3)
        # or subject-object-verb-negation patterns (4)
        elif len(matches) == 3 or len(matches) == 4:
            verb_token, subj_token, obj_token = (
                doc[matches[0]],
                doc[matches[1]],
                doc[matches[2]],
            )

            if len(matches) == 4:
                neg_token = doc[matches[3]]
                neg = neg_token.lemma_
            else:
                neg = None

            # List the SOV object's adjectival and appositional modifiers
            obj_adjectival_modifiers = " | ".join(
                w.lemma_ for w in obj_token.children if "amod" in w.dep_
            )
            obj_appositional_modifiers = " | ".join(
                w.lemma_ for w in obj_token.children if "appos" in w.dep_
            )

            # List the SOV subject's adjectival and appositional modifiers
            subj_adjectival_modifiers = " | ".join(
                w.lemma_ for w in subj_token.children if "amod" in w.dep_
            )
            subj_appositional_modifiers = " | ".join(
                w.lemma_ for w in subj_token.children if "appos" in w.dep_
            )

            row = CSVRow(
                **{
                    "subj_lemma": subj_token.lemma_,
                    "subj_adjectival_modifiers": subj_adjectival_modifiers,
                    "subj_appositional_modifiers": subj_appositional_modifiers,
                    "sub_id": subj_token.i,
                    "verb_lemma": verb_token.lemma_,
                    "verb_morph": verb_token.morph.__str__(),
                    "verb_id": verb_token.i,
                    "verb_negation": neg,
                    "obj_lemma": obj_token.lemma_,
                    "obj_adjectival_modifiers": obj_adjectival_modifiers,
                    "obj_appositional_modifiers": obj_appositional_modifiers,
                    "obj_id": obj_token.i,
                }
            )

        sov_triples.append(row)

    return sov_triples
