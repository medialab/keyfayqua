# Simple Example

## Raw data

```shell
query              ChatGPT lang:en
id                 1613784435819962368
local_time         2023-01-13T06:26:06
text               @droid254 @kay_myg Chatgpt is using 3million dollars per day mos def being bought soon
possibly_sensitive 0
retweet_count      0
like_count         1
reply_count        0
impression_count   223
lang               en
```

## Parse command

Download a Stanza English model and, as a SpaCy plug-in, use it to parse the Tweets.

```shell
>>> keyfayqua parse --datafile simple_text.csv --outfile simple_parsed.csv --lang en --model stanza --clean-social
...
2023-09-12 19:16:34 INFO: Loading these models for language: en (English):
=========================
| Processor | Package   |
-------------------------
| tokenize  | combined  |
| pos       | combined  |
| lemma     | combined  |
| depparse  | combined  |
| ner       | ontonotes |
=========================

2023-09-12 19:16:34 WARNING: GPU requested, but is not available!
2023-09-12 19:16:34 INFO: Using device: cpu
2023-09-12 19:16:34 INFO: Loading: tokenize
2023-09-12 19:16:34 INFO: Loading: pos
2023-09-12 19:16:34 INFO: Loading: lemma
2023-09-12 19:16:34 INFO: Loading: depparse
2023-09-12 19:16:34 INFO: Loading: ner
2023-09-12 19:16:35 INFO: Done loading processors!
Measuring file length ⠋ 0:00:00

Compressing output to 'simple_parsed.csv.gz'. Please wait.

Parsing... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1/1 100% 0:00:00 0:00:00
```

## Parse result

```shell
id           1613784435819962368
parsed_text  droid254 kay_myg Chatgpt is using 3million dollars per day mos def being bought soon
conll_string 1  droid254  droid254  X   GW   _   0   root  _   _
             2  kay_myg   kay_myg   X   ADD  _   1   list  _   _

             1   Chatgpt  Chatgpt  PROPN  NNP  Number=Sing                                            3   nsubj     _   _
             2   is       be       AUX    VBZ  Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin  3   aux       _   _
             3   using    use      VERB   VBG  Tense=Pres|VerbForm=Part                               0   root      _   _
             4   3        3        NUM    CD   NumForm=Digit|NumType=Card                             5   nummod    _   SpaceAfter=No
             5   million  million  NUM    CD   NumForm=Word|NumType=Card                              6   nummod    _   _
             6   dollars  dollar   NOUN   NNS  Number=Plur                                            3   obj       _   _
             7   per      per      ADP    IN   _                                                      8   case      _   _
             8   day      day      NOUN   NN   Number=Sing                                            6   nmod      _   _
             9   mos      mos      NOUN   NN   Number=Sing                                            3   obj       _   _
             10  def      def      SCONJ  IN   _                                                      12  mark      _   _
             11  being    be       AUX    VBG  VerbForm=Ger                                           12  aux:pass  _   _
             12  bought   buy      VERB   VBN  Tense=Past|VerbForm=Part|Voice=Pass                    3   advcl     _   _
             13  soon     soon     ADV    RB   Degree=Pos                                             12  advmod    _   SpaceAfter=No
```

## Compose Semgrex

For dependency relationship names in SpaCy, see [here](https://github.com/explosion/spaCy/blob/013762be4150d29ceb25d4339e8a934c32fcf195/spacy/glossary.py#L252).

`simple_semgrex.json`

```json
{
  "SOV": [
    {
      "RIGHT_ID": "verb",
      "RIGHT_ATTRS": { "POS": "VERB" }
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">",
      "RIGHT_ID": "subject",
      "RIGHT_ATTRS": { "DEP": { "IN": ["nsubj", "nsubjpass"] } }
    },
    {
      "LEFT_ID": "verb",
      "REL_OP": ">>",
      "RIGHT_ID": "object",
      "RIGHT_ATTRS": { "DEP": { "IN": ["obj", "pobj"] } }
    }
  ]
}
```

## Match command

```
>>> keyfayqua match --datafile simple_parsed.csv --matchfile simple_semgrex.json --outfile simple_sovs.csv --model stanza --lang en --spacy-language en_core_web_lg
...
=========================
| Processor | Package   |
-------------------------
| tokenize  | combined  |
| pos       | combined  |
| lemma     | combined  |
| depparse  | combined  |
| ner       | ontonotes |
=========================

2023-09-12 19:37:43 WARNING: GPU requested, but is not available!
2023-09-12 19:37:43 INFO: Using device: cpu
2023-09-12 19:37:43 INFO: Loading: tokenize
2023-09-12 19:37:43 INFO: Loading: pos
2023-09-12 19:37:43 INFO: Loading: lemma
2023-09-12 19:37:43 INFO: Loading: depparse
2023-09-12 19:37:43 INFO: Loading: ner
2023-09-12 19:37:44 INFO: Done loading processors!
      Semgrex Matches
┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Column name             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ SOV_VERB_id             │
│ SOV_VERB_lemma          │
│ SOV_VERB_pos            │
│ SOV_VERB_deprel         │
│ SOV_VERB_entity         │
│ SOV_VERB_noun_phrase    │
│ SOV_SUBJECT_id          │
│ SOV_SUBJECT_lemma       │
│ SOV_SUBJECT_pos         │
│ SOV_SUBJECT_deprel      │
│ SOV_SUBJECT_entity      │
│ SOV_SUBJECT_noun_phrase │
│ SOV_OBJECT_id           │
│ SOV_OBJECT_lemma        │
│ SOV_OBJECT_pos          │
│ SOV_OBJECT_deprel       │
│ SOV_OBJECT_entity       │
│ SOV_OBJECT_noun_phrase  │
└─────────────────────────┘
Measuring file length ⠋ 0:00:00

Compressing output to 'simple_sovs.csv.gz'. Please wait.

Matching... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1/1 100% 0:00:00 0:00:00
```

## Semgrex Results

| input                                                                                | output                 |
| ------------------------------------------------------------------------------------ | ---------------------- |
| droid254 kay_myg Chatgpt is using 3million dollars per day mos def being bought soon | Chatgpt - use - dollar |
| droid254 kay_myg Chatgpt is using 3million dollars per day mos def being bought soon | Chatgpt - use - mos    |

```
id                      1613784435819962368
SOV_VERB_id             4
SOV_VERB_lemma          use
SOV_VERB_pos            VERB
SOV_VERB_deprel         ROOT
SOV_VERB_entity
SOV_VERB_noun_phrase
SOV_SUBJECT_id          2
SOV_SUBJECT_lemma       Chatgpt
SOV_SUBJECT_pos         PROPN
SOV_SUBJECT_deprel      nsubj
SOV_SUBJECT_entity
SOV_SUBJECT_noun_phrase
SOV_OBJECT_id           7
SOV_OBJECT_lemma        dollar
SOV_OBJECT_pos          NOUN
SOV_OBJECT_deprel       obj
SOV_OBJECT_entity
SOV_OBJECT_noun_phrase

Row n°1
id                      1613784435819962368
SOV_VERB_id             4
SOV_VERB_lemma          use
SOV_VERB_pos            VERB
SOV_VERB_deprel         ROOT
SOV_VERB_entity
SOV_VERB_noun_phrase
SOV_SUBJECT_id          2
SOV_SUBJECT_lemma       Chatgpt
SOV_SUBJECT_pos         PROPN
SOV_SUBJECT_deprel      nsubj
SOV_SUBJECT_entity
SOV_SUBJECT_noun_phrase
SOV_OBJECT_id           10
SOV_OBJECT_lemma        mos
SOV_OBJECT_pos          NOUN
SOV_OBJECT_deprel       obj
SOV_OBJECT_entity
SOV_OBJECT_noun_phrase
```

# Complex Example

## Raw data

```shell
query              ChatGPT lang:en
id                 1646957012859736070
local_time         2023-04-14T19:22:05
text               I don't think chatgpt is able grasp the concept of ascii art just yet, what the actual fuck are the second and third items supposed to be? https://twitter
                   .com/askew1019/status/1646957012859736070/photo/1
possibly_sensitive 0
retweet_count      0
like_count         0
reply_count        0
impression_count   89
lang               en
```

## Parse command

Download a Stanza English model and, as a SpaCy plug-in, use it to parse the Tweets.

```shell
>>> keyfayqua parse --datafile complex_text.csv --outfile complex_parsed.csv --lang en --model stanza --clean-social
...
2023-09-13 09:21:04 INFO: Loading these models for language: en (English):
=========================
| Processor | Package   |
-------------------------
| tokenize  | combined  |
| pos       | combined  |
| lemma     | combined  |
| depparse  | combined  |
| ner       | ontonotes |
=========================

2023-09-13 09:21:04 WARNING: GPU requested, but is not available!
2023-09-13 09:21:04 INFO: Using device: cpu
2023-09-13 09:21:04 INFO: Loading: tokenize
2023-09-13 09:21:04 INFO: Loading: pos
2023-09-13 09:21:05 INFO: Loading: lemma
2023-09-13 09:21:05 INFO: Loading: depparse
2023-09-13 09:21:05 INFO: Loading: ner
2023-09-13 09:21:05 INFO: Done loading processors!
Measuring file length ⠋ 0:00:00

Compressing output to 'complex_parsed.csv.gz'. Please wait.

Parsing... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1/1 100% 0:00:00 0:00:00
```

## Parse result

```shell
id           1646957012859736070
parsed_text  I don't think chatgpt is able grasp the concept of ascii art just yet, what the actual fuck are the second and third items supposed to be?
conll_string 1   I         I        PRON   PRP  Case=Nom|Number=Sing|Person=1|PronType=Prs             4   nsubj      _   _
             2   do        do       AUX    VBP  Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin  4   aux        _   SpaceAfter=No
             3   n't       not      PART   RB   _                                                      4   advmod     _   _
             4   think     think    VERB   VB   VerbForm=Inf                                           0   root       _   _
             5   chatgpt   chatgpt  NOUN   NN   Number=Sing                                            7   nsubj      _   _
             6   is        be       AUX    VBZ  Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin  7   cop        _   _
             7   able      able     ADJ    JJ   Degree=Pos                                             4   ccomp      _   _
             8   grasp     grasp    VERB   VB   VerbForm=Inf                                           7   xcomp      _   _
             9   the       the      DET    DT   Definite=Def|PronType=Art                              10  det        _   _
             10  concept   concept  NOUN   NN   Number=Sing                                            8   obj        _   _
             11  of        of       ADP    IN   _                                                      13  case       _   _
             12  ascii     ascii    NOUN   NN   Number=Sing                                            13  compound   _   _
             13  art       art      NOUN   NN   Number=Sing                                            10  nmod       _   _
             14  just      just     ADV    RB   _                                                      15  advmod     _   _
             15  yet       yet      ADV    RB   _                                                      8   advmod     _   SpaceAfter=No
             16  ,         ,        PUNCT  ,    _                                                      4   punct      _   _
             17  what      what     PRON   WP   PronType=Int                                           26  nsubj      _   _
             18  the       the      DET    DT   Definite=Def|PronType=Art                              20  det        _   _
             19  actual    actual   ADJ    JJ   Degree=Pos                                             20  amod       _   _
             20  fuck      fuck     NOUN   NN   Number=Sing                                            26  nsubj      _   _
             21  are       be       AUX    VBP  Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin  26  cop        _   _
             22  the       the      DET    DT   Definite=Def|PronType=Art                              26  det        _   _
             23  second    second   ADJ    JJ   Degree=Pos|NumType=Ord                                 26  amod       _   _
             24  and       and      CCONJ  CC   _                                                      25  cc         _   _
             25  third     third    ADJ    JJ   Degree=Pos|NumType=Ord                                 23  conj       _   _
             26  items     item     NOUN   NNS  Number=Plur                                            4   parataxis  _   _
             27  supposed  suppose  VERB   VBN  Tense=Past|VerbForm=Part                               26  acl        _   _
             28  to        to       PART   TO   _                                                      29  mark       _   _
             29  be        be       AUX    VB   VerbForm=Inf                                           27  xcomp      _   SpaceAfter=No
             30  ?         ?        PUNCT  .    _                                                      4   punct      _   SpaceAfter=No
```

## Match command

Try the simple Semgrex S-O-V pattern.

```shell
>>> keyfayqua match --datafile complex_parsed.csv --matchfile simple_semgrex.json --outfile complex_sovs.csv --model stanza --lang en --spacy-language en_core_web_lg
...
=========================
| Processor | Package   |
-------------------------
| tokenize  | combined  |
| pos       | combined  |
| lemma     | combined  |
| depparse  | combined  |
| ner       | ontonotes |
=========================

2023-09-13 09:24:30 WARNING: GPU requested, but is not available!
2023-09-13 09:24:30 INFO: Using device: cpu
2023-09-13 09:24:30 INFO: Loading: tokenize
2023-09-13 09:24:30 INFO: Loading: pos
2023-09-13 09:24:30 INFO: Loading: lemma
2023-09-13 09:24:30 INFO: Loading: depparse
2023-09-13 09:24:30 INFO: Loading: ner
2023-09-13 09:24:31 INFO: Done loading processors!
      Semgrex Matches
┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Column name             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ SOV_VERB_id             │
│ SOV_VERB_lemma          │
│ SOV_VERB_pos            │
│ SOV_VERB_deprel         │
│ SOV_VERB_entity         │
│ SOV_VERB_noun_phrase    │
│ SOV_SUBJECT_id          │
│ SOV_SUBJECT_lemma       │
│ SOV_SUBJECT_pos         │
│ SOV_SUBJECT_deprel      │
│ SOV_SUBJECT_entity      │
│ SOV_SUBJECT_noun_phrase │
│ SOV_OBJECT_id           │
│ SOV_OBJECT_lemma        │
│ SOV_OBJECT_pos          │
│ SOV_OBJECT_deprel       │
│ SOV_OBJECT_entity       │
│ SOV_OBJECT_noun_phrase  │
└─────────────────────────┘
Measuring file length ⠋ 0:00:00

Compressing output to 'complex_sovs.csv.gz'. Please wait.

Matching... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1/1 100% 0:00:00 0:00:00

```

## Match Result

| input                                                                                                                      | output              |
| -------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| I don't think chatgpt is able grasp the concept of ascii art just yet, what the actual fuck are the second and third items | I - think - concept |

```shell
id                      1646957012859736070
SOV_VERB_id             3
SOV_VERB_lemma          think
SOV_VERB_pos            VERB
SOV_VERB_deprel         ROOT
SOV_VERB_entity
SOV_VERB_noun_phrase
SOV_SUBJECT_id          0
SOV_SUBJECT_lemma       I
SOV_SUBJECT_pos         PRON
SOV_SUBJECT_deprel      nsubj
SOV_SUBJECT_entity
SOV_SUBJECT_noun_phrase
SOV_OBJECT_id           9
SOV_OBJECT_lemma        concept
SOV_OBJECT_pos          NOUN
SOV_OBJECT_deprel       obj
SOV_OBJECT_entity
SOV_OBJECT_noun_phrase
```

---

## Improve Semgrex

For dependency relationship names in SpaCy, see [here](https://github.com/explosion/spaCy/blob/013762be4150d29ceb25d4339e8a934c32fcf195/spacy/glossary.py#L252).

```json
{
  "SOV": [
    {
      "RIGHT_ID": "root",
      "RIGHT_ATTRS": { "DEP": { "IN": ["root", "ccomp"] } }
    },
    {
      "LEFT_ID": "root",
      "REL_OP": ">",
      "RIGHT_ID": "subject",
      "RIGHT_ATTRS": { "DEP": { "IN": ["nsubj", "nsubjpass"] } }
    },
    {
      "LEFT_ID": "root",
      "REL_OP": ">>",
      "RIGHT_ID": "object",
      "RIGHT_ATTRS": { "DEP": { "IN": ["obj", "pobj"] } }
    }
  ]
}
```

## Re-run match command

```shell
>>> keyfayqua match --datafile complex_parsed.csv --matchfile complex_semgrex.json --outfile complex_sovs.csv --model stanza --lang en --spacy-language en_core_web_lg
```

## New Result

| input                                                                                                                      | output                   |
| -------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| I don't think chatgpt is able grasp the concept of ascii art just yet, what the actual fuck are the second and third items | chatgpt - able - concept |

```
id                      1646957012859736070
SOV_ROOT_id             6
SOV_ROOT_lemma          able
SOV_ROOT_pos            ADJ
SOV_ROOT_deprel         ccomp
SOV_ROOT_entity
SOV_ROOT_noun_phrase
SOV_SUBJECT_id          4
SOV_SUBJECT_lemma       chatgpt
SOV_SUBJECT_pos         NOUN
SOV_SUBJECT_deprel      nsubj
SOV_SUBJECT_entity
SOV_SUBJECT_noun_phrase
SOV_OBJECT_id           9
SOV_OBJECT_lemma        concept
SOV_OBJECT_pos          NOUN
SOV_OBJECT_deprel       obj
SOV_OBJECT_entity
SOV_OBJECT_noun_phrase
```

# Thoughts

It's still not good enough. We wanted to capture : `chatgpt` - `grasp` - `concept`. Instead, we got `chatgpt` - `able` - `concept`. This is because we targeted the tokens that related to others as a "root" or as a "ccomp" (clausal complement). In our example sentence, the "ccomp" is the word `able`. The verb we wanted to target, `grasp`, is a "xcomp" (open clausal complement). But how can we generalize our search of subject-object-verb triplets while capturing this sort of phrase?

_Help! Bring in the linguist!_
