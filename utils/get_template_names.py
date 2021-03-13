import pywikibot
import json
import sys

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print('Insert the code of the template as command line argument')
        exit(0)
    site = pywikibot.Site("wikidata", "wikidata")
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, sys.argv[1])
    item_dict = item.get()
    item_dict = item_dict['labels']
    item_dict = item_dict.toJSON()
    cleaned_dict = set()
    for key in item_dict:
        el = item_dict[key]['value'].lower().encode('utf8').decode()
        if ':' in el:
            el = el.split(':')[1]
        cleaned_dict.add(el)
    with open('{}.json'.format(sys.argv[1]), 'w') as f:
        f.write(json.dumps(list(cleaned_dict), ensure_ascii=False))