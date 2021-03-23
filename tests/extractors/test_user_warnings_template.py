import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', 'wikidump'))
import collections
from wikidump.extractors import user_warnings_template

INPUT_TEXT = """
<noinclude>{{Protetta}}</noinclude>
{| width="85%" align="center" style="background:#FFFFFF; padding:0.5em; border:1px solid #FFFF00; min-height:90px;"
|-
| [[File:Yellow card.svg|60px|left]]
| Gentile {{ROOTPAGENAME}},
al prossimo contributo contrario alle [[Wikipedia:Raccomandazioni_e_linee_guida|linee guida di Wikipedia]] scatterà un [[Wikipedia:Politiche di blocco degli utenti|'''<span style="color:#FF0000; font-size:130%">blocco</span>''']] in scrittura sulla tua utenza, pertanto questo è l'ultimo invito a collaborare in modo costruttivo. 

Per favore, rispetta il lavoro altrui: segui le [[Aiuto:Cosa mettere su Wikipedia|regole]] e usa il [[Wikipedia:buon senso|buon senso]].{{#if:{{{1|}}}|<br />{{{1}}} }}
|}<noinclude>
=== Template correlati ===
* [[Wikipedia:Gestione del vandalismo#Template di avviso]]
* [[Template:Rc]]

[[Categoria:Template vandalismo|Yc]]
</noinclude>


"""

def wikibreaks_extractor():
    new_regex = user_warnings_template.userwarnings_regex_extractor(INPUT_TEXT)
    print('{}'.format(new_regex))

if __name__ == "__main__":
    wikibreaks_extractor()