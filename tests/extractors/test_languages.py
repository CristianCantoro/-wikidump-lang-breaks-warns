from wikidump.extractors import language
from wikidump.extractors.common import Identifier

import collections

INPUT_TEXT = '''
Good morning!
I am a new Wikipedian, while looking for the definition of [[humorism]].
{{Babel-5|ca|es-3|en-2|it-2|it-1}}
Deserunt nostrud enim ad culpa enim nostrud enim irure laborum commodo voluptate proident labore ea do dolor irure adipisicing 
veniam voluptate sint incididunt quis excepteur cupidatat labore officia veniam deserunt.
{{Utente en-5}}
{{Utente it}}
{{Utente es-2}}
Nulla cupidatat laboris minim velit id adipisicing ex voluptate et ullamco duis aute irure nostrud 
velit cillum anim sit voluptate non esse labore proident cillum Lorem ea enim veniam quis ex in mollit aliquip nisi ea anim aute ipsum reprehenderit.
{{Babel|en|it-4|es-2|ca-1}}
'''

EXPECTED_KNOWLEDGE = [
    language.LanguageLevel('ca', language.LanguageLevel.MOTHER_TONGUE_LEVEL),
    language.LanguageLevel('es', 3),
    language.LanguageLevel('en', 2),
    language.LanguageLevel('it', 2),
    language.LanguageLevel('it', 1),
    language.LanguageLevel('en', 5),
    language.LanguageLevel('it', language.LanguageLevel.MOTHER_TONGUE_LEVEL),
    language.LanguageLevel('es', 2),
    language.LanguageLevel('en', language.LanguageLevel.MOTHER_TONGUE_LEVEL),
    language.LanguageLevel('it', 4),
    language.LanguageLevel('es', 2),
    language.LanguageLevel('ca', 1),
]

EXPECTED_LANGS = 4

def test_language_knowledge():
    langs = (lang for lang, _ in language.language_knowledge(INPUT_TEXT)).sort()
    found_langs = collections.Counter(l.lang for l in langs)

    assert found_langs == EXPECTED_LANGS

    for l_k in EXPECTED_KNOWLEDGE.sort():
        assert langs == l_k