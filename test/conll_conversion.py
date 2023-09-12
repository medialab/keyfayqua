from src.main import setup_parser
from src.parsers import ConLLParser
import unittest
from spacy.tokens.doc import Doc


MISSING_LEMMA_BATCH = [
    (
        "Research preview of our newest model: ChatGPT We're trying something new with this preview: Free and immediately available for everyone (no waitlist!) « OpenAI: Try talking with ChatGPT, our new AI system which is optimized for dialogue. Your feedback will help us improve it. — »",
        1,
    ),
    (
        "VillaJakeF1 There are already a number of tools that can detect it. I’ve been using chatGPT a bit recently to get coding snippets, and I have to say a lot of it is either incomplete or incorrect. I wouldn’t want to rely on it for something as important as a thesis. But it is early days still",
        2,
    ),
]


class LegitimateString(unittest.TestCase):
    def test_missing_lemma(self):
        dep_parser = setup_parser(lang="en")
        conll_parser = ConLLParser(lang="en")
        for doc, _ in dep_parser.pipe(batch=MISSING_LEMMA_BATCH, batch_size=1):
            conll_str = doc._.conll_str
            doc = conll_parser(conll_str)
            assert isinstance(doc, Doc)


if __name__ == "__main__":
    unittest.main()
