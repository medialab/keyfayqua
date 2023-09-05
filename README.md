# Qui fait quoi ?

## Tools to detect subject-object-verb triples in French and English

Using open-source dependency parser models trained on French and English, `keyfayqua`'s [main program](src/__main__.py`) produces data about subject-object-verb (SOV) triples in sentences. Optionally, the program can also retrieve words dependent on a target word anywhere in the sentence.

## Install

1. Create and activate a virtual Python environment (>=3.11).
2. Clone this repository.

```shell
git clone https://github.com/medialab/keyfayqua.git
```

3. Install `keyfayqua` in the activated virtual environment.

```
pip install -e .
```

## Usage

### Parse dependency relationships

```shell
 Usage: keyfayqua parse [OPTIONS]

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --datafile            FILE     [default: None] [required]                                                                                                                           │
│ *  --outfile             PATH     Path to file with Conll results [default: None] [required]                                                                                           │
│ *  --id-col              TEXT     ID column name [default: None] [required]                                                                                                            │
│ *  --text-col            TEXT     Text column name [default: None] [required]                                                                                                          │
│    --lang                [en|fr]  [default: SupportedLang.en]                                                                                                                          │
│    --clean-social                                                                                                                                                                      │
│    --help                         Show this message and exit.                                                                                                                          │
╰────────────────────────────────────────────────────────────────────
```
