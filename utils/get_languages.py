# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

"""Retrives the supported languages in Wikipedia and prints them"""

import requests
from lxml import html

def extract_languages(page):
    pass

if __name__ == "__main__":
    res = requests.get('https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes')
    if res.status_code == 200:
        extract_languages(html.fromstring(res.content))
    else:
        print('Something went wrong with the page retrival status code {}'.format(res.status_code))