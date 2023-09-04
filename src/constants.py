from pathlib import Path

from casanova import namedrecord
from spacy.symbols import (
    VERB,
    advmod,
    agent,
    amod,
    appos,
    csubj,
    dobj,
    iobj,
    neg,
    nsubj,
    nsubjpass,
    obj,
    obl,
)

OUTDIR = Path("output")


fields = [
    "subj_lemma",
    "subj_adjectival_modifiers",
    "subj_appositional_modifiers",
    "sub_id",
    "verb_lemma",
    "verb_morph",
    "verb_id",
    "verb_negation",
    "obj_lemma",
    "obj_adjectival_modifiers",
    "obj_appositional_modifiers",
    "obj_id",
    "target",
    "target_id",
    "target_modifier",
    "target_modifier_pos",
    "target_modifier_deprel",
    "target_modifier_id",
]


HOPSPARSER_MODEL = "models/UD_all_spoken_French-flaubert"


CSVRow = namedrecord(
    "CSVRow", fields=fields, defaults=[None for _ in range(len(fields))]
)


ANCHOR_TARGET_PATTERN = {"RIGHT_ID": "anchor_modifier_pattern", "RIGHT_ATTRS": {}}


MODIFIER_PATTERN = {
    "LEFT_ID": "anchor_modifier_pattern",
    "REL_OP": ">>",
    "RIGHT_ID": "modifier",
    "RIGHT_ATTRS": {"DEP": {"IN": [amod, appos]}},
}


ANCHOR_VERB_PATTERN = {"RIGHT_ID": "anchor_verb", "RIGHT_ATTRS": {"POS": VERB}}


NEGATION_PATTERN = {
    "LEFT_ID": "anchor_verb",
    "REL_OP": ">",
    "RIGHT_ID": "negation",
    "RIGHT_ATTRS": {"DEP": neg},
}


SUBJECT_PATTERN = {
    "LEFT_ID": "anchor_verb",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": {"IN": [nsubjpass, nsubj]}},
}


OBJECT_PATTERN = {
    "LEFT_ID": "anchor_verb",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": {"IN": [obj, dobj, iobj]}},
}
