# Credit to BERTweet. I've copied their TweetNormalizer and made some modifications.
# https://github.com/VinAIResearch/BERTweet/blob/master/TweetNormalizer.py

import re

import emoji
from nltk.tokenize import TweetTokenizer
from ural.patterns import URL_IN_TEXT_RE

tokenizer = TweetTokenizer()


def normalizeToken(token):
    if token.startswith("#"):
        return
    elif len(token) == 1 and emoji.is_emoji(token):
        return ""
    else:
        if token == "’":
            return "'"
        elif token == "…":
            return "..."
        else:
            return token


def normalizer(text):
    # Remove trailing white space
    text = text.strip()

    # Remove emojis
    text = emoji.replace_emoji(text, replace="")

    # Separate titles / pre-colon spans from sentences
    text = re.sub(r"(^(\w+\W+){1,2})*:", "\\1.", text)

    # Remove URLs
    text = URL_IN_TEXT_RE.sub(repl="", string=text)

    # Remove user citatation (i.e. "via @theregister")
    text = re.sub(r"(?!https)via(\s{0,}@\w*)", "", text)

    # Remove user handles and hashtags
    text = re.sub(r"[@#]", "", text)

    return text
