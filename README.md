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

Result:

```text
1	ChatGPT-4	chatgpt-4	PROPN	ADJ	Gender=Fem|Number=Sing	0	ROOT	_	_
2	.	.	PUNCT	PUNCT	_	1	punct	_	_

1	plus	plus	ADV	ADV	_	4	advmod	_	_
2	de	de	ADP	ADP	_	3	case	_	_
3	1000	1000	NUM	PRON	NumType=Card	1	iobj	_	_
4	prompts	prompt	NOUN	VERB	Tense=Pres|VerbForm=Part	0	ROOT	_	_
5	pour	pour	ADP	ADP	_	6	mark	_	_
6	améliorer	améliorer	VERB	VERB	VerbForm=Inf	4	acl	_	_
7	votre	votre	DET	DET	Number=Sing|Poss=Yes	8	det	_	_
8	création	création	NOUN	NOUN	Gender=Fem|Number=Sing	6	obj	_	_
9	https	https	INTJ	PROPN	Gender=Masc|Number=Sing	8	nmod	_	SpaceAfter=No
10	.	.	PUNCT	PUNCT	_	4	punct	_	SpaceAfter=No

```
