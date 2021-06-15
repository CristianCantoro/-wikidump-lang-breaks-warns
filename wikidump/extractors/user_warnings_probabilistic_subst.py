"""
https://it.wikipedia.org/wiki/Trie
https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm
"""

import ahocorasick
import regex as re
from typing import Iterable, Mapping, Mapping, Tuple
from .. import user_warnings_ca, user_warnings_en, user_warnings_es, user_warnings_it
from .types.user_warnings_token import UserWarningTokens
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import Stemmer
import bisect
from backports.datetime_fromisoformat import MonkeyPatch
import ahocorasick
import datetime

# Polyfiller for retrocompatibiliy with Python3.5
MonkeyPatch.patch_fromisoformat()

class KeyList(object):
    def __init__(self, l, key):
        self.l = l
        self.key = key
    def __len__(self):
        return len(self.l)
    def __getitem__(self, index):
        return self.key(self.l[index])

# template category mapping dictionary
template_category_mapping = dict()
template_category_mapping.update(user_warnings_ca.plantilles_mapping)
template_category_mapping.update(user_warnings_es.plantillas_mapping)
template_category_mapping.update(user_warnings_en.template_mappings)
template_category_mapping.update(user_warnings_it.templates_mapping)

# exports 
__all__ = ['extract_probabilistic_user_warning_templates', 'extract_probabilistic_user_warning_templates_last_revision', 'UserWarningTokens']

def extract_probabilistic_user_warning_templates(
    text: str, 
    language: str,
    timestamp: str,
    templates_dictionary: Mapping,
    use_stemmer: bool) -> Iterable[UserWarningTokens]:

    # candidates templates
    candidates_template = dict()                # candidate templates with occurences
    words_found = set()                         # all the words that matches
    templates_found = list()                    # templates found
    words_mapping_current_timestamp = dict()    # collection of words of a given template at the revision timestamp

    # clean text
    text = clean_text(text, language, use_stemmer)
    
    # revision date
    revision_date = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

    # build the template trie
    template_trie, words_mapping_current_timestamp = build_trie_current_timestamp(templates_dictionary, revision_date)

    # No template available at that time
    if not template_trie:
        return list()
    
    # Search the words thanks to the rie and aho-corasick algorithm
    for _, (templates, word) in template_trie.iter(text):
        for referred_template in templates:
            if not referred_template in candidates_template:
                candidates_template[referred_template] = 0
            candidates_template[referred_template] += 1
        words_found.add(word)


    # check if the words collected are part of certain templates
    for template in candidates_template:
        # words that are part of a revision of a particolar template
        template_at_that_timestamp = words_mapping_current_timestamp[template]
        # check if the template is present for real
        words_list,_ = template_at_that_timestamp
        if words_found.issuperset(set(words_list)):
            # add the found template
            templates_found.append(UserWarningTokens(template.lower(), template_category_mapping[template.lower()]))
    return templates_found


def extract_probabilistic_user_warning_templates_last_revision(
    text: str, 
    language: str,
    timestamp_first: datetime.datetime,
    timestamp_last: datetime.datetime,
    templates_dictionary: Mapping,
    use_stemmer: bool) -> Iterable[UserWarningTokens]:
    
    # candidates templates
    candidates_template = dict()                # candidate templates with occurences
    words_found = set()                         # all the words that matches
    templates_found = list()                    # templates found
    words_mapping = dict()                      # collection of words of a given template at the revision timestamp

    # clean text
    text = clean_text(text, language, use_stemmer)

    # build the template trie (not for a given timestamp but from the first timestamp to the last timestamp)
    template_trie, words_mapping = build_trie_from_to(templates_dictionary, timestamp_first, timestamp_last)
    
    # No template available at that time
    if not template_trie:
        return list()

    # Search the words thanks to the rie and aho-corasick algorithm
    for _, (templates, word) in template_trie.iter(text):
        for referred_template in templates:
            if not referred_template in candidates_template:
                candidates_template[referred_template] = 0
            candidates_template[referred_template] += 1
        words_found.add(word)

    # check if the words collected are part of certain templates
    for template in candidates_template:
        # words that are part of all revision of a particular template
        templates_words_list = words_mapping[template]
        # for each list of words and timestamp
        for template_wl in templates_words_list:
            words_list,_ = template_wl
            # check if it is contained for real
            if words_found.issuperset(set(words_list)):
                # add the found template
                templates_found.append(UserWarningTokens(template.lower(), template_category_mapping[template.lower()]))
                # exit the loop, because the template was found
                break

    return templates_found

def build_trie_current_timestamp(template_dictionary: Mapping, timestamp: datetime.datetime) -> Tuple[ahocorasick.Automaton, Mapping]:
    """Function which builds the trie from the previous mapping by the specified timestamp"""
    trie = ahocorasick.Automaton()              # trie
    words_mapping_current_timestamp = dict()
    word_templates = dict()
    # collect the words and the template associated (a list of them if multiple template is associated)
    for template in template_dictionary: 
        # list of words of the template at that given timestamp
        template_at_that_timestamp = find_previous_timestamp(template_dictionary[template], timestamp)
        # if it exists
        if template_at_that_timestamp != None:
            template_at_that_timestamp = template_dictionary[template][template_at_that_timestamp]
            words_mapping_current_timestamp[template] = template_at_that_timestamp  # current word list at that timestamp
            words_list,_ = template_at_that_timestamp
            # for each word
            for word in words_list:
                if not word in word_templates:
                    word_templates[word] = list()
                # templates referring to that template
                word_templates[word].append(template)

    for word in word_templates:
        trie.add_word(word, (word_templates[word], word))   # key is the word to search, value is the template
    trie.make_automaton()

    if not word_templates:
        return None, None

    return trie, words_mapping_current_timestamp

def build_trie_from_to(template_dictionary: Mapping, from_timestamp: datetime.datetime, to_timestamp: datetime.datetime) -> Tuple[ahocorasick.Automaton, Mapping]:
    """Function which builds the trie from the first timestamp tot the last one given"""
    trie = ahocorasick.Automaton()
    words_mapping = dict()  # words mapping
    word_templates = dict() # words template
    # collect the words and the template associated (a list of them if multiple template is associated)
    for template in template_dictionary:
        # index first template to consider
        index_first_timestamp = find_previous_timestamp(template_dictionary[template], from_timestamp) or 0
        # for all the revisions of that template starting from the first date possible
        for index in range(index_first_timestamp, len(template_dictionary[template])):
            
            words_list, t_stamp = template_dictionary[template][index]

            # stop the iteration because we overcome the to_timestamp limit
            if t_stamp > to_timestamp:
                break

            if not template in words_mapping:
                words_mapping[template] = list()
            words_mapping[template].append(template_dictionary[template][index])  # word lists for that template
            for word in words_list:
                if not word in word_templates:
                    word_templates[word] = list()
                word_templates[word].append(template)
            
    for word in word_templates:
        trie.add_word(word, (word_templates[word], word))   # key is the word to search, value is the template
    trie.make_automaton()

    if not word_templates:
        return None, None

    return trie, words_mapping

def find_previous_timestamp(elem_list: Iterable[Tuple[str, datetime.datetime]], current_timestamp: datetime.datetime):
    '''Find greatest item less or equal to key knowing that the list are ordered by timestamp'''
    i = bisect.bisect_left(KeyList(elem_list, key=lambda x: x[1]), current_timestamp)
    if i == len(elem_list):
        i = i - 1
    if elem_list[i][1] != current_timestamp:
        i = i - 1
    if i < 0: 
        return None
    return i

def clean_text(text: str, language: str, use_stemmer: bool) -> str:
    """Clean the string to be iterated"""
    stemmer = Stemmer.Stemmer(language)
    text = re.sub(r'[^\w]', ' ', text)
    text = ' '.join(list(word for word in word_tokenize(text) if not word in stopwords.words(language)))
    if use_stemmer:
        return ' '.join(list(map(stemmer.stemWord, word_tokenize(text))))
    else:
        return text