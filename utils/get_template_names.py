# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

"""Simple scraper which retrives the supported languages in Wikipedia and prints them"""

import requests
import json
import sys
from lxml import html

TEMPLATE_NAME = set()

def extract_template(content, lang, title):
    try:
        title = content.xpath('//h1/text()')[0]
        TEMPLATE_NAME.add(title.split(':')[1])
    except:
        print('No {} found for {}'.format(title, lang))
        
def write_json(l):
    with open('{}.json'.format(sys.argv[1]), 'w') as f:
        f.write(json.dumps(l, ensure_ascii=False).encode('utf8').decode())

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print('Insert the name of the template as command line argument')
        exit(0)

    # sys.argv[1] = sys.argv[1].title()
    f = open('iso_639_1.json', )
    languages = json.load(f)
    f.close()
    for lang in languages:
        try:
            res = requests.get('https://{}.wikipedia.org/wiki/Template:{}'.format(lang, sys.argv[1]))
            if res.status_code == 200:
                extract_template(html.fromstring(res.content), lang, sys.argv[1])
        except:
            print('https://{}.wikipedia.org/wiki/Template:{} does not exists'.format(lang, sys.argv[1]))
    write_json(list(TEMPLATE_NAME))