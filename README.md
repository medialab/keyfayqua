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

4. On Mac, whose MPS GPU is not yet supported, I recommend you install two additional libraries to (slightly) improve performace:
   - `pip install thinc-apple-ops`
   - `pip install spacy[apple]`

## Usage

### Parse dependency relationships

```shell
 Usage: keyfayqua parse [OPTIONS]

╭─ Options ─────────────────────────────────────────────────────────╮
│ *  --datafile            FILE     [default: None] [required]      │
│ *  --outfile             PATH     Path to file with Conll results │
│                                   [default: None]                 │
│                                   [required]                      │
│    --id-col              TEXT     ID column name [default: id]    │
│    --text-col            TEXT     Text column name                │
│                                   [default: text]                 │
│    --lang                [en|fr]  [default: SupportedLang.en]     │
│    --clean-social                                                 │
│    --help                         Show this message and exit.     │
╰───────────────────────────────────────────────────────────────────╯
```

The `parse` command parses the text documents in the in-file and outputs a CSV file with the NLP results serialized in a CoNLL-formatted string. This string can subsequently be reconverted into a SpaCy document or its information can be extracted using any number of tools that rely on the standardized [CoNLL format](https://universaldependencies.org/format.html).

The `parse` command requires the path to the in-file and a path to the out-file CSV. Upon completion or exit of the program, the out-file CSV will be compressed using Gzip. The out-file is expected to be very large despite having only 4 columns: (1) an identifier for the text document, given with the option `--id-col`, (2) the original text, given with the option `--text-col`, (3) the version of the text that was parsed (`parsed_text`), and (4) the CoNLL string.

The original text may be cleaned if the flag `--clean-social` is provided with the `parse` command. This flag adds an extra step in which the text is pre-processed with a [normalizing script](src/normalizer.py) designed for social media text documents, specifically Tweets. The normalizer applies the following changes:

1. remove trailing white space

```python
>>> text = ' Trailing white space at beginning.'
>>> text.strip()
'Trailing white space at beginning.'
```

1. remove emojis

```python
>>> import emoji
>>>
>>> text = '#FTLV 📆 20-22 sept. : initiation à la paléographie, proposée par l’@Ecoledeschartes-@psl_univ dans le cadre de la #formationcontinue. Inscriptions jusqu’au 10 sept. ➡️ https://lc.cx/VQNpZE'
>>>
>>> emoji.replace_emoji(text, replace='')
'#FTLV  20-22 sept. : initiation à la paléographie, proposée par l’@Ecoledeschartes-@psl_univ dans le cadre de la #formationcontinue. Inscriptions jusqu’au 10 sept.  https://lc.cx/VQNpZE'
```

2. separate titles / pre-colon spans from sentences [`(^(\w+\W+){1,2})*:`]

```python
>>> import re
>>>
>>> text = '#FTLV  20-22 sept. : initiation à la paléographie, proposée par l’@Ecoledeschartes-@psl_univ dans le cadre de la #formationcontinue. Inscriptions jusqu’au 10 sept.  https://lc.cx/VQNpZE'
>>>
>>> re.sub(r'(^(\w+\W+){1,2})*:', '\\1.', text)
'#FTLV  20-22 sept. . initiation à la paléographie, proposée par l’@Ecoledeschartes-@psl_univ dans le cadre de la #formationcontinue. Inscriptions jusqu’au 10 sept.  https.//lc.cx/VQNpZE'
```

3. remove URLs

```python
>>> from ural.patterns import URL_IN_TEXT_RE
>>>
>>> text = '#FTLV  20-22 sept. . initiation à la paléographie, proposée par l’@Ecoledeschartes-@psl_univ dans le cadre de la #formationcontinue. Inscriptions jusqu’au 10 sept.  https.//lc.cx/VQNpZE'
>>>
>>> URL_IN_TEXT_RE.sub(repl='HTTPURL', string=text)
'#FTLV  20-22 sept. . initiation à la paléographie, proposée par l’@Ecoledeschartes-@psl_univ dans le cadre de la #formationcontinue. Inscriptions jusqu’au 10 sept.  https.'
```

4. remove # and @ signs [`[@#]`]

```python
>>> import re
>>>
>>> text = '#FTLV  20-22 sept. . initiation à la paléographie, proposée par l’@Ecoledeschartes-@psl_univ dans le cadre de la #formationcontinue. Inscriptions jusqu’au 10 sept.  https.'
>>>
>>>re.sub(r'[@#]', '',  text)
'FTLV  20-22 sept. . initiation à la paléographie, proposée par l’Ecoledeschartes-psl_univ dans le cadre de la formationcontinue. Inscriptions jusqu’au 10 sept.  https.'
```

5. remove citations at the end of a post [`(?!https)via(\s{0,}@\w*)`]

```python
>>> import re
>>>
>>> text = 'ChatGPT-4 . plus de 1000 prompts pour améliorer votre création de contenu http. via @siecledigital'
>>>
>>> re.sub(r"(?!https)via(\s{0,}@\w*)", "", text)
'ChatGPT-4 . plus de 1000 prompts pour améliorer votre création de contenu http. '
```

6. normalize apostrophes and elipses

7. normalize spaces in English-language temporal markers (`a.m.`, `p.m.`)
