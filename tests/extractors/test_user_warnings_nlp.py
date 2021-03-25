import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', 'wikidump'))
import collections
from wikidump.extractors import user_warnings_template_words

INPUT_TEXT = """
{{Metacaixa d'avís discussió
| tipus     = avís
| imatge    = [[Fitxer:Fairytale date.png|40px]]
| estil     = 
| estiltext = 
| text      = Si desitgeu realitzar aportacions al '''calendari d'esdeveniments''' o a la '''taula anual''', us recomanem que consulteu prèviament el [[Viquipèdia:Llibre d'estil del calendari d'esdeveniments i de les taules anuals|llibre d'estil del calendari d'esdeveniments i de les taules anuals]], per tal de seguir el mateix format a tots els articles.}}<noinclude>
{{ús de la plantilla|contingut=
Avís per posar en les pàgines de discussió dels articles sobre calendari d'esdeveniments (anys...)
}}
"""

def wikibreaks_extractor():
    new_regex = user_warnings_template_words.userwarnings_words_extractor(INPUT_TEXT)
    print('{}'.format(new_regex))

if __name__ == "__main__":
    wikibreaks_extractor()