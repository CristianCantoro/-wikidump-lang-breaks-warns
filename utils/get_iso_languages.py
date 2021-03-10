# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

"""Simple scraper which retrives the supported languages in Wikipedia and prints them"""

import requests
import json
from lxml import html

ISO_LANG = dict()

def extract_languages(content):
    rows = content.xpath('//table[@id="Table"]/tbody/tr[position()>1]')
    for r in rows:
        iso_lang_name = r.xpath('.//td[3]//text()')[0].split(',')[0] # only the first name
        iso_repr = [ r.xpath('.//td[5]//text()'), r.xpath('.//td[6]//text()'), r.xpath('.//td[7]//text()'), r.xpath('.//td[8]//text()') ]
        for iso in iso_repr:
            if iso:
                ISO_LANG[iso[0]] = iso_lang_name
        


def write_json(dictionary):
    with open('iso_langs.json', 'w') as f:
        f.write(json.dumps(dictionary))

if __name__ == "__main__":
    res = requests.get('https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes')
    if res.status_code == 200:
        extract_languages(html.fromstring(res.content))
        write_json(ISO_LANG)
    else:
        print('Something went wrong with the page retrival status code {}'.format(res.status_code))