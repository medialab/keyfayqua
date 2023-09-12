class SpacyDownloadException(Exception):
    def __init__(self, e, lang: str):
        self.e = e
        self.lang = lang

    def __str__(self):
        msg = """
        You need to download the SpaCy language for {}. See SpaCy's documentation here: https://spacy.io/usage/models#languages
        """.format(
            self.lang
        )
        return msg


class StanzaDownloadException(Exception):
    def __init__(self, e, lang: str):
        self.e = e
        self.lang = lang

    def __str__(self):
        msg = """
        Stanza attempted to download a language model for '{}' but encounterd the following error:

{}

        Please make sure you're connected to the internet and using a valid language prefix.
        """.format(
            self.lang, self.e
        )
        return msg
