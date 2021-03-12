from wikidump.extractors import languages
from wikidump.extractors.common import Identifier

import collections

INPUT_TEXT = '''
{{Babel-2| it}}
'''

EXPECTED_KNOWLEDGE = [
]

EXPECTED_LANGS = 4

def test_language_knowledge():
    langs = list(lang for lang, _ in languages.language_knowledge(INPUT_TEXT))
    print(langs)

if __name__ == "__main__":
    test_language_knowledge()