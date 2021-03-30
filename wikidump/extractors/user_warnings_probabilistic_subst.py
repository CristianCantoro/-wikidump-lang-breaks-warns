"""
https://it.wikipedia.org/wiki/Trie
https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm
"""

import ahocorasick
import regex as re
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional, Mapping
from .common import CaptureResult, Identifier, Span
from .types.user_warnings_token import UserWarningTokens
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import Stemmer
import datetime

# exports 
__all__ = ['extract_probabilistic_user_warning_templates', 'UserWarningTokens']

def extract_probabilistic_user_warning_templates(
    text: str, 
    language: str,
    timestamp: str,
    template_trie: ahocorasick.Automaton, 
    templates_dictionary: Mapping) -> Iterable[UserWarningTokens]:
    
    # candidates templates
    candidates_template = set()     # candidate templates
    words_found = set()             # all the words that matches
    templates_found = list()        # templates found
    go_next_template = False        # if the current template is found or go next template

    # clean text
    text = clean_text(text, language)

    # Search the words thanks to the rie and aho-corasick algorithm
    for _, (referred_template, word) in template_trie.iter(text):
        candidates_template.add(referred_template)
        words_found.add(word)
    
    # revision date
    revision_date = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

    # check if the words collected are part of certain templates
    # know that the revisions are ordered by timestamp I can prune something 
    for template in candidates_template:
        go_next_template = False
        # words that are part of a revision of a particolar template
        for words_lists, template_timestamp in templates_dictionary[template]:
            template_date = datetime.datetime.fromisoformat(template_timestamp.replace('Z', '+00:00')) 
            if revision_date > template_date:
                # the template could not have been substituted
                go_next_template = True 
            elif words_found.issuperset(set(words_lists)):
                # if superset then all the value are contained in tghe words found
                go_next_template = True
                # add the found template
                templates_found.append(UserWarningTokens(template, words_lists))
            # to skip that template (already found)
            if go_next_template:
                break
    return templates_found

def clean_text(text: str, language: str) -> str:
    """Clean the string to be iterated"""
    #stemmer = Stemmer.Stemmer(language)
    text = re.sub(r'[^\w]', ' ', text)
    return ' '.join(list(word for word in word_tokenize(text) if not word in stopwords.words(language)))
    #return ' '.join(list(map(stemmer.stemWord, word_tokenize(text))))