# Qui fait quoi ?

## Tools to detect syntactic relationships in French and English

`keyfayqua` is a Command Line tool that features 2 commands. First, the `parse` command annotates a corpus of texts, detecting entities and dependency relationships, and outputs each document's annotations as a [CoNLL-formatted](https://universaldependencies.org/format.html) string in the column of a CSV file. Second, the `match` command reconverts the CoNLL string into a SpaCy object and, using [Semgrex patterns](https://aclanthology.org/2023.tlt-1.7/) and SpaCy's [`DependencyMatcher`](https://spacy.io/api/dependencymatcher/), detects dependency relationships between nodes in the parsed sentences. By providing Semgrex patterns, the user chooses the types of relationships that will be searched with the `match` command.

1. [How to install](#install)
2. [How to use](#usage)
   1. [`parse` command](#parse-dependency-relationships) (intially parse the text documents)
   2. [`test-conll` command](#test-conll-string-validity) (test CoNLL string validity)
   3. [`match` comand](#match-dependency-patterns) (apply Semgrex patterns to match syntactic relationships)
   4. [Match output](#match-output)
3. [Optional pre-processing](#optional-pre-processing)

---

The idea is that you'll use the `parse` command only one time on the corpus, achieving a stable set of the annotations, and then apply various Semgrex patterns with the `match` command. Consequently, you could also apply the `match` command and test out your Semgrex patterns on any corpus whose document annotations have been written and stored in the CoNLL format. For example, if you manage to parse a corpus with any transformer model you like and then convert the model output into a CoNLL format, you can provide that data to the `match` command and apply your Semgrex patterns. The reason to use the CoNLL format, rather than a SpaCy `DocBin`, for instance, is that it can (theoretically) be generalized across many model types.

`keyfayqua`'s `parse` command takes advantage of SpaCy's Python architecture as well as high-performance dependency parsers specially trained for French and English. For French, we use one of Loïc Grobol and Benoît Crabbés [Hopsparser models](https://zenodo.org/record/7703346/). For English, we use Stanford NLP's [Stanza model](https://github.com/stanfordnlp/stanza).

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
pip install --upgrade pip
pip install -e .
```

4. On Mac, whose MPS GPU is not yet supported, I recommend you install two additional libraries to (slightly) improve performace:
   - `pip install thinc-apple-ops`
   - `pip install spacy[apple]`

## Usage

### Parse dependency relationships

The `parse` command is the first step to detecting dependency relationship patterns. It takes in a corpus of text documents and outputs CoNLL-formatted string representations of the parsed documents.

Provide the command a path to the text corpus (`--datafile`), a path to the desired out-file (`--outfile`), the name of the column that holds a unique identifier for the document (`--id-col`), the name of the column that holds the text (`--text-col`), and the primary language of the corpus (`--lang`). Optionally, you can tell the `parse` command that you want to [pre-process](#optional-pre-processing) the text with a cleaning script designed for social media posts, specifically Twitter.

```shell
 Usage: keyfayqua parse [OPTIONS]

╭─ Options ───────────────────────────────────────────────────╮
│ *  --datafile            FILE     [default: None]           │
│                                   [required]                │
│ *  --outfile             PATH     Path to file with Conll   │
│                                   results                   │
│                                   [default: None]           │
│                                   [required]                │
│    --id-col              TEXT     ID column name            │
│                                   [default: id]             │
│    --text-col            TEXT     Text column name          │
│                                   [default: text]           │
│    --lang                [en|fr]  [default:                 │
│                                   SupportedLang.en]         │
│    --clean-social                                           │
│    --batch-size          INTEGER  [default: 5000]           │
│    --model-path          TEXT                               │
│    --help                         Show this message and     │
│                                   exit.                     │
╰─────────────────────────────────────────────────────────────╯

```

_Note about French:_

> By selecting the French language, you'll be asked if you have already downloaded a Hopsparser model and where you've stored it. If you do not have a Hopsparser model, the script will download one for you. The default model is the [`Flaubert` model for Spoken french](https://zenodo.org/record/7703346/files/UD_all_spoken_French-flaubert.tar.xz?download=1) and the default download location is in this repository at `./hopsparser_model/UD_all_spoken_French-flaubert/`. Upon repeated uses of the `parse` command on French-language corpora, you can provide this path to the downloaded model, or the path to wherever you've moved the model. If you want to use another of the Hopsparser models, you can download it yourself and provide the path when prompted after calling the `parse` command. If you don't want to be prompted at all while parsing French, you can directly declare the path to the Hopsparser model with the option `--model-path`.

Upon completion or exit of the `parse` command, the CSV file to which the program had been writing each text document's annotations will be compressed using Gzip. The out-file is expected to be very large despite having only 3 columns:

1. an identifier for the text document, given with the option `--id-col`
2. the version of the text that was parsed
3. the CoNLL-formatted string

### Test CoNLL string validity

Sometimes it's useful to quickly test the validity and integrity of your corpus's CoNLL-formatted strings, before proceding to the `match` command and applying Semgrex patterns. With the command `test-conll`, test the `spacy_conll` conversion from CoNLL string to SpaCy doc on your dataset.

```shell

╭─ Options ───────────────────────────────────────────────────╮
│ *  --datafile         FILE  Path to file with Conll results │
│                             [default: None]                 │
│                             [required]                      │
│    --conll-col        TEXT  CoNLL string column name        │
│                             [default: conll_string]         │
│    --help                   Show this message and exit.     │
╰─────────────────────────────────────────────────────────────╯

```

### Match dependency patterns

After creating a data file with annotated tokens correctly written in a CoNLL format, you're ready to apply Semgrex matches and detect syntactic relationships.

First, you'll need a JSON file with a set of Semgrex match patterns. See an example [here](#composing-the-semgrex-file). Then, you'll call the `match` command.

```shell
 Usage: keyfayqua match [OPTIONS]

╭─ Options ─────────────────────────────────────────────────╮
│ *  --datafile          FILE     Path to file with Conll   │
│                                 results                   │
│                                 [default: None]           │
│                                 [required]                │
│ *  --matchfile         FILE     Name of JSON file in      │
│                                 semgrex folder            │
│                                 [default: None]           │
│                                 [required]                │
│ *  --outfile           PATH     Path to file with         │
│                                 dependency matches        │
│                                 [default: None]           │
│                                 [required]                │
│    --id-col            TEXT     ID column name            │
│                                 [default: id]             │
│    --conll-col         TEXT     CoNLL string column name  │
│                                 [default: conll_string]   │
│    --lang              [en|fr]  [default:                 │
│                                 SupportedLang.en]         │
│    --model-path        TEXT                               │
│    --help                       Show this message and     │
│                                 exit.                     │
╰───────────────────────────────────────────────────────────╯

```

The option `--datafile` points to the CSV with the parsed text. `--matchfile` points to your JSON file of Semgrex patterns. `--outfile` points to the CSV file you want to produce, which contain the match results. Due to the potentially large size of the results, the out-file will only retain from the input data file each text document's unique ID, rather than also its parsed text, CoNLL string, and/or other columns. Declare the ID column with the option `--id-col`. By default, the `match` command will look for the CoNLL string in the column `conll_string`, so if the data file uses another name for that column provide it with the option `--conll-col`.

Finally, you should also declare the parsed text's primary langauge. SpaCy's DependencyMatcher requires a vocabulary in order to optimally parse the CoNLL information. Declare the language with the option `--lang`, entering either "fr" for French or "en" for English.

#### Match output

The CSV output by the `match` command is dynamically formatted to have as many columns as are necessary to store information about the patterns you provide. A Semgrex pattern has at least 2 nodes, an anchor and something that relates to it. For every node in the pattern, there will be 6 columns.

1. `PatternName_NodeName_id` : the token's index
2. `PatternName_NodeName_lemma` : the token's lemma (or text if the model failed to lemmatize it)
3. `PatternName_NodeName_pos` : the token's part-of-speech tag
4. `PatternName_NodeName_deprel` : the token's dependency relationship to its head
5. `PatternName_NodeName_entity` : the token's named-entity-recognition label
6. `PatternName_NodeName_noun_phrase` (in development)

Each match on a Semgrex pattern is written to a row of the CSV, along with the text document's unique ID.

| id                  | FindRootSubjects_ROOT_id | FindRootSubjects_ROOT_lemma | FindRootSubjects_ROOT_pos | FindRootSubjects_ROOT_deprel | FindRootSubjects_ROOT_entity | FindRootSubjects_ROOT_noun_phrase | FindRootSubjects_SUBJECT_id | FindRootSubjects_SUBJECT_lemma | FindRootSubjects_SUBJECT_pos | FindRootSubjects_SUBJECT_deprel | FindRootSubjects_SUBJECT_entity | FindRootSubjects_SUBJECT_noun_phrase |
| ------------------- | ------------------------ | --------------------------- | ------------------------- | ---------------------------- | ---------------------------- | --------------------------------- | --------------------------- | ------------------------------ | ---------------------------- | ------------------------------- | ------------------------------- | ------------------------------------ |
| 1598065358522699776 | 18                       | launch                      | VERB                      | ROOT                         |                              |                                   | 17                          | we                             | PRON                         | nsubj                           |                                 |                                      |

### Composing the Semgrex file

The `match` command requires a JSON file with valid Semgrex patterns. The JSON must be composed of key-value pairs in which the key is the name of the Semgrex pattern and its value is an array of the nodes in the pattern.

The JSON format closely resembles the format SpaCy uses for their DependencyMatcher. Below, we've taken [the example in their documentation](https://spacy.io/usage/rule-based-matching#dependencymatcher) and translated it into the JSON format. It's essentially the same. Rather than attribute the list of dictionaries to a Python object, we assign it to a key, the pattern name (`"PatternName"`) in the JSON. Read SpaCy's documentation on the DependencyMatcher for more information.

```json
{
  "PatternName": [
    {
      "RIGHT_ID": "founded",
      "RIGHT_ATTRS": { "ORTH": "founded" }
    },
    {
      "LEFT_ID": "founded",
      "REL_OP": ">",
      "RIGHT_ID": "subject",
      "RIGHT_ATTRS": { "DEP": "nsubj" }
    },
    {
      "LEFT_ID": "founded",
      "REL_OP": ";",
      "RIGHT_ID": "initially",
      "RIGHT_ATTRS": { "ORTH": "initially" }
    }
  ]
}
```

### Optional pre-processing

The original text may be cleaned if the flag `--clean-social` is provided with the `parse` command. This flag adds an extra step in which the text is pre-processed with a [normalizing script](src/utils/normalizer.py) designed for social media text documents, specifically Tweets. The normalizer applies the following changes:

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
