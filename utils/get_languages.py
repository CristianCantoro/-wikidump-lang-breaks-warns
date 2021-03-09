# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

"""Retrives the supported languages in Wikipedia and prints them"""

import requests

if __name__ == "__main__":
    res = requests.get('https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes')
    print(res.text)
    print(res.status_code)