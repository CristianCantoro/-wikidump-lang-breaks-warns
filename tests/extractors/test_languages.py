import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', 'wikidump'))
import collections
from wikidump.extractors import languages
from wikidump.extractors.common import Identifier

INPUT_TEXT = '''
{{Babel|ca|es-4|en-2|an-1|ast-1|fr-1|gl-1|it-1|la-1|pt-1}}

{{any de naixement|1991}}
{{Viquipedista dels PPCC}}
{{Viquipedista berguedà}}
{{Viquipedista roig}}
{{Patumaire}}
{{Seguidor Bàsquet Manresa}}
{{Lector Tolkien}}
{{Ska}}
{{Metal}}
{{System Of A Down}}
{{Usuari last.fm}}
{{Ateu}}
{{Viquipedista socialista}}
{{Republicà}}
{{Viquipedista independentista PPCC}}
{{Antifeixista}}
{{Viquipedista de la CUP}}

[[Categoria:Viquipedistes del Berguedà]]

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
    exit(0)
    langs.sort()

    found_langs = set(l.lang for l in langs)
    print(found_langs)
    
    assert len(found_langs) == EXPECTED_LANGS

    for l_k in EXPECTED_KNOWLEDGE.sort():
        assert langs == l_k 

if __name__ == "__main__":
    test_language_knowledge()