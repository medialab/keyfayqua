# Credit to BERTweet. I've copied their TweetNormalizer and made some modifications.
# https://github.com/VinAIResearch/BERTweet/blob/master/TweetNormalizer.py

import emoji
from nltk.tokenize import TweetTokenizer
import re


tokenizer = TweetTokenizer()


def normalizeToken(token):
    lowercased_token = token.lower()
    if token.startswith("@"):
        return re.sub(r"@", "", token)
    if token.startswith("#"):
        return re.sub(r"#", "", token)
    elif lowercased_token.startswith("http") or lowercased_token.startswith("www"):
        return "HTTPURL"
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
    # Remove user citatation (i.e. "via @theregister")
    tweet = re.sub(r"(?!http)via(\s{0,}@[a-z]*)", "", tweet)

    # Remove trailing white space
    tweet = tweet.strip()

    # Normalize apostrophes
    tokens = tokenizer.tokenize(tweet.replace("’", "'").replace("…", "..."))

    # Clean tokens
    normTweet = " ".join([normalizeToken(token) for token in tokens])

    # Normalize English-language conjunctions
    normTweet = (
        normTweet.replace("cannot ", "can not ")
        .replace("n't ", " n't ")
        .replace("n 't ", " n't ")
        .replace("ca n't", "can't")
        .replace("ai n't", "ain't")
    )
    normTweet = (
        normTweet.replace("'m ", " 'm ")
        .replace("'re ", " 're ")
        .replace("'s ", " 's ")
        .replace("'ll ", " 'll ")
        .replace("'d ", " 'd ")
        .replace("'ve ", " 've ")
    )
    normTweet = (
        normTweet.replace(" p . m .", "  p.m.")
        .replace(" p . m ", " p.m ")
        .replace(" a . m .", " a.m.")
        .replace(" a . m ", " a.m ")
    )

    return " ".join(normTweet.split())
