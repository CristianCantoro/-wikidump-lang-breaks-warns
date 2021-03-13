import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', 'wikidump'))
import collections
from wikidump.extractors import languages
from wikidump.extractors.common import Identifier

INPUT_TEXT = '''
<div class="toccolours itwiki_template_babelbox">
<div class="intestazione">[[Wikipedia:Babel]]</div>
{{Utente __it}}
{{Utente __en-2}}
{{Utente __sc}}
'''

EXPECTED_KNOWLEDGE = [
    languages.LanguageLevel('ca', languages.LanguageLevel.MOTHER_TONGUE_LEVEL),
    languages.LanguageLevel('es', 3),
    languages.LanguageLevel('en', 2),
    languages.LanguageLevel('it', 2),
    languages.LanguageLevel('it', 1),
    languages.LanguageLevel('en', 5),
    languages.LanguageLevel('it', languages.LanguageLevel.MOTHER_TONGUE_LEVEL),
    languages.LanguageLevel('es', 2),
    languages.LanguageLevel('en', languages.LanguageLevel.MOTHER_TONGUE_LEVEL),
    languages.LanguageLevel('it', 4),
    languages.LanguageLevel('es', 2),
    languages.LanguageLevel('ca', 1),
]

EXPECTED_LANGS = 4

def test_language_knowledge():
    langs = list(lang for lang,_ in languages.language_knowledge(INPUT_TEXT))
    print(langs)
    langs.sort()

    found_langs = set(l.lang for l in langs)
    print(found_langs)
    
    assert len(found_langs) == EXPECTED_LANGS

    for l_k in EXPECTED_KNOWLEDGE.sort():
        assert langs == l_k 

if __name__ == "__main__":
    test_language_knowledge()