# Credit to BERTweet. I've copied their TweetNormalizer and made some modifications.
# https://github.com/VinAIResearch/BERTweet/blob/master/TweetNormalizer.py

import re

import emoji
from nltk.tokenize import TweetTokenizer
from ural.patterns import URL_IN_TEXT_RE

tokenizer = TweetTokenizer()


def normalizeToken(token):
    if token.startswith("#"):
        return re.sub(r"#", "", token)
    elif len(token) == 1 and emoji.is_emoji(token):
        return ""
    else:
        if token == "’":
            return "'"
        elif token == "…":
            return "..."
        else:
            return token


def normalizer(tweet):
    # Remove trailing white space
    tweet = tweet.strip()

    # Separate titles / pre-colon spans from sentences
    tweet = re.sub(r"(^(\w+\W+){1,2})*:", "\\1.", tweet)

    # Remove URLs
    tweet = URL_IN_TEXT_RE.sub(repl="", string=tweet)

    # Normalize apostrophes
    tokens = tokenizer.tokenize(tweet.replace("’", "'").replace("…", "..."))

    # Clean tokens
    normTweet = " ".join([normalizeToken(token) for token in tokens])

    # Remove user citatation (i.e. "via @theregister")
    tweet = re.sub(r"(?!HTTPURL)via(\s{0,}@\w*)", "", tweet)

    # Remove user handles
    normTweet = re.sub(r"@", "", normTweet)

    normTweet = (
        normTweet.replace(" p . m .", "  p.m.")
        .replace(" p . m ", " p.m ")
        .replace(" a . m .", " a.m.")
        .replace(" a . m ", " a.m ")
    )

    return " ".join(normTweet.split())
