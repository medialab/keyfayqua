from pathlib import Path

from casanova import namedrecord

NS = None

OUTDIR = Path("output")

fields = [
    "voice",
    "subject_lemma",
    "verb_lemma",
    "object_lemma",
]


CSVRow = namedrecord(
    "CSVRow", fields=fields, defaults=[None for _ in range(len(fields))]
)
