# Qui fait quoi ?

## Tools to detect subject-object-verb triples in French and English

`keyfayqua` is a Command Line tool that features 2 commands. First, the `parse` command annotates a corpus of texts, detecting entities and dependency relationships, and outputs each document's annotations as a [CoNLL-formatted](https://universaldependencies.org/format.html) string in the column of a CSV file. Second, the `match` command reconverts the CoNLL string into a SpaCy object and, using [Semgrex patterns](https://aclanthology.org/2023.tlt-1.7/) and SpaCy's [`DependencyMatcher`](https://spacy.io/api/dependencymatcher/), detects dependency relationships between nodes in the parsed sentences. By providing Semgrex patterns, the user chooses the types of relationships that will be searched with the `match` command.

`keyfayqua` takes advantage of SpaCy's Python architecture as well as high-performance dependency parsers specially trained for French and English. For French, we use one of Loïc Grobol and Benoît Crabbés [Hopsparser models](https://zenodo.org/record/7703346/). For English, we use Stanford NLP's [Stanza model](https://github.com/stanfordnlp/stanza). Because `keyfayqua` relies on SpaCy and because Stanford NLP has developed a `spacy-stanza` plug-in, any of [Stanza's models](https://stanfordnlp.github.io/stanza/available_models.html) can theoretically be used during the `parse` command, though this feature isn't yet added.

#### Hopsparser (French)

```bibtex
@inproceedings{grobol:hal-03223424,
    title = {{Analyse en dépendances du français avec des plongements contextualisés}},
    author = {Grobol, Loïc and Crabbé, Benoît},
    url = {https://hal.archives-ouvertes.fr/hal-03223424},
    booktitle = {{Actes de la 28ème Conférence sur le Traitement Automatique des Langues Naturelles}},
    eventtitle = {{TALN-RÉCITAL 2021}},
    venue = {Lille, France},
    pdf = {https://hal.archives-ouvertes.fr/hal-03223424/file/HOPS_final.pdf},
    hal_id = {hal-03223424},
    hal_version = {v1},
}
```

#### Stanza (English)

```bibtex
@inproceedings{qi2020stanza,
    title={Stanza: A {Python} Natural Language Processing Toolkit for Many Human Languages},
    author={Qi, Peng and Zhang, Yuhao and Zhang, Yuhui and Bolton, Jason and Manning, Christopher D.},
    booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics: System Demonstrations",
    year={2020}
}
```

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

The `parse` command is the first step to detecting dependency relationship patterns. It takes in a corpus of text documents and outputs CoNLL-formatted string representations of the parsed documents.

Provide the command a path to the text corpus (`--datafile`), a path to the desired out-file (`--outfile`), the name of the column that holds a unique identifier for the document (`--id-col`), the name of the column that holds the text (`--text-col`), and the primary language of the corpus (`--lang`). Optionally, you can tell the `parse` command that you want to [pre-process](#pre-processing) the text with a cleaning script designed for social media posts, specifically Twitter.

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

_Note about French:_

> By selecting the French language, you'll be asked if you have already downloaded a Hopsparser model and where you've stored it. If you do not have a Hopsparser model, the script will download one for you. The default model is the [`Flaubert` model for Spoken french](https://zenodo.org/record/7703346/files/UD_all_spoken_French-flaubert.tar.xz?download=1) and the default download location is in this repository at `./hopsparser_model/UD_all_spoken_French-flaubert/`. Upon repeated uses of the `parse` command on French-language corpora, you can provide this path to the downloaded model, or the path to wherever you've moved the model. If you want to use another of the Hopsparser models, you can download it yourself and provide the path when prompted after calling the `parse` command.

Upon completion or exit of the `parse` command, the CSV file to which the program had been writing each text document's annotations will be compressed using Gzip. The out-file is expected to be very large despite having only 4 columns:

1. an identifier for the text document, given with the option `--id-col`
2. the original text, given with the option `--text-col`
3. the version of the text that was parsed
4. the CoNLL-formatted string

#### Pre-processing

The original text may be cleaned if the flag `--clean-social` is provided with the `parse` command. This flag adds an extra step in which the text is pre-processed with a [normalizing script](src/normalizer.py) designed for social media text documents, specifically Tweets. The normalizer applies the following changes:

1. remove emojis

```python
>>> import emoji
>>>
>>> text = 'ChatGPT-4 : plus de 1000 prompts 🤯 pour améliorer votre #création https://openai.com/blog/chatgpt via @siecledigital'
>>>
>>> emoji.replace_emoji(text, replace='')
'ChatGPT-4 : plus de 1000 prompts  pour améliorer votre #création https://openai.com/blog/chatgpt via @siecledigital'
```

2. separate titles / pre-colon spans from sentences [`(^(\w+\W+){1,2})*:`]

```python
>>> import re
>>>
>>> text = 'ChatGPT-4 : plus de 1000 prompts  pour améliorer votre #création https://openai.com/blog/chatgpt via @siecledigital'
>>>
>>> re.sub(r'(^(\w+\W+){1,2})*:', '\\1.', text)
'ChatGPT-4 . plus de 1000 prompts  pour améliorer votre #création https.//openai.com/blog/chatgpt via @siecledigital'
```

3. remove URLs

```python
>>> from ural.patterns import URL_IN_TEXT_RE
>>>
>>> text = 'ChatGPT-4 . plus de 1000 prompts  pour améliorer votre #création https.//openai.com/blog/chatgpt via @siecledigital'
>>>
>>> URL_IN_TEXT_RE.sub(repl='', string=text)
'ChatGPT-4 . plus de 1000 prompts  pour améliorer votre #création https. via @siecledigital'
```

4. remove citations at the end of a post [`(?!https)via(\s{0,}@\w*)`]

```python
>>> import re
>>>
>>> text = 'ChatGPT-4 . plus de 1000 prompts  pour améliorer votre #création https. via @siecledigital'
>>>
>>> re.sub(r"(?!https)via(\s{0,}@\w*)", "", text)
'ChatGPT-4 . plus de 1000 prompts  pour améliorer votre #création https. '
```

5. remove # and @ signs [`[@#]`]

```python
>>> import re
>>>
>>> text = 'ChatGPT-4 . plus de 1000 prompts  pour améliorer votre #création https. '
>>>
>>>re.sub(r'[@#]', '',  text)
'ChatGPT-4 . plus de 1000 prompts  pour améliorer votre création https. '
```

6. remove trailing white space

```python
>>> text = 'ChatGPT-4 . plus de 1000 prompts  pour améliorer votre création https. '
>>>
>>> text.strip()
'ChatGPT-4 . plus de 1000 prompts  pour améliorer votre création https.'
```

7. remove double spaces

```python
>>> text = 'ChatGPT-4 . plus de 1000 prompts  pour améliorer votre création https.'
>>>
>>> re.sub(r'\s+', ' ', text)
'ChatGPT-4 . plus de 1000 prompts pour améliorer votre création https.'
```

Original text:

> ChatGPT-4 : plus de 1000 prompts 🤯 pour améliorer votre #création https://openai.com/blog/chatgpt via @siecledigital

Cleaned text:

> ChatGPT-4 . plus de 1000 prompts pour améliorer votre création https.'

CoNLL result:

| ID  | FORM      | LEMMMA    | UPOS  | XPOS  | FEATS                     | HEAD | DEPREL | DEPS | MISC |
| --- | --------- | --------- | ----- | ----- | ------------------------- | ---- | ------ | ---- | ---- |
| 1   | ChatGPT-4 | chatgpt-4 | PROPN | ADJ   | Gender=Fem \| Number=Sing | 0    | ROOT   | \_   | \_   |
| 2   | .         | .         | PUNCT | PUNCT | \_                        | 1    | punct  | \_   | \_   |

| ID  | FORM      | LEMMMA    | UPOS  | XPOS  | FEATS                       | HEAD | DEPREL | DEPS | MISC |
| --- | --------- | --------- | ----- | ----- | --------------------------- | ---- | ------ | ---- | ---- |
| 1   | plus      | plus      | ADV   | ADV   | \_                          | 4    | advmod | \_   | \_   |
| 2   | de        | de        | ADP   | ADP   | \_                          | 3    | case   | \_   | \_   |
| 3   | 1000      | 1000      | NUM   | PRON  | NumType=Card                | 1    | iobj   | \_   | \_   |
| 4   | prompts   | prompt    | NOUN  | VERB  | Tense=Pres \| VerbForm=Part | 0    | ROOT   | \_   | \_   |
| 5   | pour      | pour      | ADP   | ADP   | \_                          | 6    | mark   | \_   | \_   |
| 6   | améliorer | améliorer | VERB  | VERB  | VerbForm=Inf                | 4    | acl    | \_   | \_   |
| 7   | votre     | votre     | DET   | DET   | Number=Sing \| Poss=Yes     | 8    | det    | \_   | \_   |
| 8   | création  | création  | NOUN  | NOUN  | Gender=Fem \| Number=Sing   | 6    | obj    | \_   | \_   |
| 9   | https     | https     | INTJ  | PROPN | Gender=Masc \| Number=Sing  | 8    | nmod   | \_   | \_   |
| 10  | .         | .         | PUNCT | PUNCT | \_                          | 4    | punct  | \_   | \_   |
