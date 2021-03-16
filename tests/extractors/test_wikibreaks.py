import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', 'wikidump'))
import collections
from wikidump.extractors import wikibreaks

INPUT_TEXT = '''
{{wikibreak|[[Io sono un link|bellissimo!|come va|sample text]]|[[discrepàncies|ciao|]] devo essere incluso!| io sto tutto apposto grazie}}
{{viquidescansas|samuele|epic}}
{{occupato||sono in sessione||}}
{{tentata wikipausa}}
{{wikipausa corta|name=Samuele|ciao|come va|type=epico|back=10/10/2020}}
'''

EXPECTED_LANGS = 4

def wikibreaks_extractor():
    wbreaks = list(wb for wb,_ in wikibreaks.wikibreaks_extractor(INPUT_TEXT))
    for w_b in wbreaks:
        print(w_b, '\n')

if __name__ == "__main__":
    wikibreaks_extractor()