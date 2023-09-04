# Qui fait quoi ?

## Tools to detect subject-object-verb triples in French and English

Using open-source dependency parser models trained on French and English, `keyfayqua`'s [main program](src/__main__.py`) produces data about subject-object-verb (SOV) triples in sentences. Optionally, the program can also retrieve words dependent on a target word anywhere in the sentence.

### Results

The subject in the SOV can be an active nominal subject, a passive nominal subject, an oblique nominal, a clausal subject, or the agent that complements a passive verb. The subject must direclty depend on the verb and an object must depend on the verb too.

The object in the SOV triple can be either a direct object or an indirect object. In order to form the SOV, the object must directly depend on a verb and the verb must have a subject that directly depends on it.

The target can be any word, though the program was designed to search for nouns, i.e. "ChatGPT."

For every SOV triple or pair between the target and a dependent word, the program writes a line to a CSV with the following data fields:

- Subject in SOV
  - Lemma (`subj_lemma`)
  - [Adjectival modifiers](https://universaldependencies.org/u/dep/amod.html) (`subj_adjectival_modifiers`)
  - [Appositional modifiers](https://universaldependencies.org/u/dep/appos.html) (`subj_appositional_modifiers`)
  - Index of token's first character in the sentence (`sub_idx`)
- Verb in SOV
  - Lemma (`verb_lemma`)
  - [Morphological features](https://universaldependencies.org/u/feat/index.html) (`verb_morph`)
  - Index of token's first character in the sentence (`verb_idx`)
  - If present, token negating the verb (`verb_negation`)
- Object in SOV
  - Lemma (`obj_lemma`)
  - [Adjectival modifiers](https://universaldependencies.org/u/dep/amod.html) (`obj_adjectival_modifiers`)
  - [Appositional modifiers](https://universaldependencies.org/u/dep/appos.html) (`obj_appositional_modifiers`)
  - Index of token's first character the sentence (`obj_idx`)
- Target word (if given)
  - Lemma of targeted token (`target`)
  - Index of token's first character in the sentence (`target_idx`)
- Modifier of target word (if given)
  - Lemma of token that modifies the target (`target_modifier`)
  - [Part-of-speech](https://universaldependencies.org/u/pos/index.html) tag of the token (`target_modifier_pos`)
  - [Syntactic relationship](https://universaldependencies.org/u/dep/index.html) or dependency relationship between the modifier and the target (`target_modifier_deprel`)
    - [adverbial modifier](https://universaldependencies.org/u/dep/advmod.html) (advmod)
    - [adjectival modifier](https://universaldependencies.org/u/dep/amod.html) (amod)
    - [appositional modifier](https://universaldependencies.org/u/dep/appos.html) (appos)
  - Index of the token's first character in the sentence

### Parsers

The program takes advantage of state-of-the-art dependency parsers, which vary by language, as well as SpaCy's standard data structure for dealing with the results of various parsers. It's the best of both worlds, both particularized and universal. To process English-language text, the program uses SpaCy's [`spacy-stanza`](https://github.com/explosion/spacy-stanza) plug-in, which deploys models from Stanford NLP's Stanza parser. To process French-langauge text, the program uses a SpaCy plug-in for [`hopsparser`](https://github.com/hopsparser/hopsparser), which was developed by Loïc Grobol and Benoît Crabbé. Eventually, parsers for other languages can be added if they work in a [SpaCy pipeline](https://spacy.io/usage/processing-pipelines) and/or produce a SpaCy document object.

#### Stanza

```bibtex
@inproceedings{qi2020stanza,
    title={Stanza: A {Python} Natural Language Processing Toolkit for Many Human Languages},
    author={Qi, Peng and Zhang, Yuhao and Zhang, Yuhui and Bolton, Jason and Manning, Christopher D.},
    booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics: System Demonstrations",
    year={2020}
}
```

#### Hopsparser

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

## Set up

First, set up a virtual environment in Python v. 3.11 and give it a name.

Clone this repository and change to that new directory.

```shell
git clone https://github.com/medialab/keyfayqua.git
cd keyfayqua
```

Then install the necessary Python dependencies, models, as well as the Hopsparser repository, which is not yet deployed with `pip install`.

```shell
bash scripts/install.sh
```

The install script will create 2 directories at the root of `keyfayqua`.

- `resources/` will hold the clone of a fork of the Hopsparser repository that I made, which contains a correction to a dependency in the program's setup script.
- `models/` will contain the Flaubert-FTB Universal Dependencies model, downloaded from [Zenodo](https://zenodo.org/record/7703346/) where Loïc Grobol published pre-trained Hopsparser models.

## Usage

At minimum, to run the program, you will need to call the `src/__main__.py` script and give the path to a CSV file that contains the text you want to parse.

```shell
python src/__main__.py TEXTFILE
```

Depending on the use case, you can ammend the above command with options for cleaning the text if it's from social media (removing hashtags, user handles, etc.) with the flag `--cleaning-social` and/or provide a word you want to target with the option `--target`.

```shell
python src/__main__.py TEXTFILE --target ChatGPT --cleaning-social
```

After entering one of the above commands, you will be prompted to complete other necessary information. The following options are prompted so as to make calling the command easier for the user.

```shell
ID column name :
>> id
Text column name :
>> text
Select the language of the text ('en', 'fr')
>> fr
What name do you want to give the out-file?
>> french_tweets.csv
```

You can give the values of the above options directly in the initial command if you wish to skip the prompt.

```shell
python src/__main__.py TEXTFILE --cleaning-social --target ChatGPT --id-col id --text-col text --lang fr --out-file french_tweets.csv
```

The program will make a directory called `output/` at the root of this repository. It will contain a subdirectory, whose name is the abbreviation of the entered language, and that subdirectory will contain a file for the results, i.e. `./output/fr/french_tweets.csv`, and a file that stores the parsed document's Conll representation, `./output/fr/french_tweets_conll.csv`. The latter file is generated so that the model's predictions, which are expensive to produce, are not lost. The Conll string representation can subsequently be [parsed and reconverted into a SpaCy document](https://spacy.io/universe/project/spacy-conll/) for future data manipulation.
