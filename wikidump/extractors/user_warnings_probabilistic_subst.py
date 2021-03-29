"""
https://it.wikipedia.org/wiki/Trie
https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm
"""

import ahocorasick
import regex as re
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional, Mapping
from .common import CaptureResult, Identifier, Span
from .types.user_warnings_probabilistic_subst import UserWarningTokens
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import Stemmer

# exports 
__all__ = ['extract_probabilistic_user_warning_templates', 'UserWarningTokens']

def extract_probabilistic_user_warning_templates(
    text: str, 
    language: str,
    template_trie: ahocorasick.Automaton, 
    templates_dictionary: Mapping) -> Iterable[UserWarningTokens]:
    
    # candidates templates
    candidates_template = set()     # candidate templates
    words_found = set()             # all the words that matches
    templates_found = list()        # templates found
    found_template = False          # if the current template is found

    # clean text
    text = clean_text(text, language)

    # Search the words thanks to the rie and aho-corasick algorithm
    for _, (referred_template, word) in template_trie.iter(text):
        candidates_template.add(referred_template)
        words_found.add(word)
    
    # check if the words collected are part of certain templates
    for template in candidates_template:
        found_template = False
        for words_lists in templates_dictionary[template]:
            # words that are part of a revision of a particolar template
            for w_list in words_lists:
                if words_found.issuperset(set(w_list)):
                    # if superset then all the value are contained inn tghe words found
                    found_template = True
                    # add the found template
                    templates_found.append(UserWarningTokens(template, w_list))
                # to skip that template (already found)
                if found_template:
                    break
            # skip that template already found
            if found_template:
                break 
    return templates_found

def clean_text(text: str, language: str) -> str:
    """Clean the string to be iterated"""
    stemmer = Stemmer.Stemmer(language)
    text = re.sub(r'[^\w]', ' ', text)
    text = ' '.join(list(word for word in word_tokenize(text) if not word in stopwords.words(language)))
    return ' '.join(list(map(stemmer.stemWord, word_tokenize(text))))