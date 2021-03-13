import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', 'wikidump'))
import collections
from wikidump.extractors import languages
from wikidump.extractors.common import Identifier

INPUT_TEXT = '''
{{capçalera d'etiquetes|Així sóc jo}}
{{Viquipedista de Catalunya}}
{{Biotecnòleg}}
<center>\'\'\'Babel\'\'\'</center>
{{Babel ca}}
{{Babel es}}
{{Babel en-1}}
{{Babel af-0}}
{{Babel ar-0}}
{{Babel bg-0}}
{{Babel cs-0}}
{{Babel el-0}}
{{Babel eu-0}}
{{Babel ga-0}}
{{Babel haw-0}}
{{Babel id-0}}
{{Babel nn-0}}
{{Babel no-0}}
{{Babel sw-0}}

{{Vandalitzat|6}}
{{tancament d'etiquetes}}

===Projectes===
*\'\'\'Viquiprojecte personal: Enllaços a la portada de qualitat\'\'\'. Que tots els enllaços de la portada no només estiguin en blau sinó a més apuntant cap a articles de qualitat que impresionin i empenyin a la gent a participar activament. M'ajudarà a aconseguir-ho la \'\'\'[[/Laboratori:Portada|màquina del temps]]\'\'\'.

*[[Portal:Catalunya]]
*[[Portal:Biotecnologia]] (em sap greu haver-ho deixat abandonat durant tant de temps)

*[[/Calaix de sastre|Calaix de sastre]]

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