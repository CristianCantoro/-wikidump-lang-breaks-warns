# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

"""Simple scraper which retrives the supported languages in Wikipedia and prints them"""

import requests
import json
from lxml import html

ISO_LANG = dict()
ISO_639_1 = dict()
ISO_639_2_T = dict()
ISO_639_2_B = dict()
ISO_639_3 = dict()

def extract_languages(content):
    rows = content.xpath('//table[@id="Table"]/tbody/tr[position()>1]')
    for r in rows:
        iso_lang_name = r.xpath('.//td[3]//text()')[0].split(',')[0] # only the first name
        iso_repr = [ r.xpath('.//td[5]//text()'), r.xpath('.//td[6]//text()'), r.xpath('.//td[7]//text()'), r.xpath('.//td[8]//text()') ]
        for iso in iso_repr:
            if iso:
                ISO_LANG[iso[0]] = iso_lang_name
        if iso_repr[0]:
            ISO_639_1[iso_repr[0][0]] = iso_lang_name
        if iso_repr[1]:
            ISO_639_2_T[iso_repr[1][0]] = iso_lang_name
        if iso_repr[2]:
            ISO_639_2_B[iso_repr[2][0]] = iso_lang_name
        if iso_repr[3]:
            ISO_639_3[iso_repr[3][0]] = iso_lang_name
        
def write_json(dictionary, name):
    with open('{}.json'.format(name), 'w') as f:
        f.write(json.dumps(dictionary, ensure_ascii=False).encode('utf8').decode())

if __name__ == "__main__":
    res = requests.get('https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes')
    if res.status_code == 200:
        extract_languages(html.fromstring(res.content))
        write_json(ISO_LANG, 'iso_lang')
        write_json(ISO_639_1, 'iso_639_1')
        write_json(ISO_639_2_T, 'iso_639_2_t')
        write_json(ISO_639_2_B, 'iso_639_2_b')
        write_json(ISO_639_3, 'iso_639_2_3')
    else:
        print('Something went wrong with the page retrival status code {}'.format(res.status_code))