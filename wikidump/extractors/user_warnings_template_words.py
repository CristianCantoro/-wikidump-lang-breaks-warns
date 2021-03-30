import regex as re
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional, Mapping
from .common import CaptureResult, Identifier, Span
from .types.user_warnings_tf import UserWarningTf
import mwparserfromhell

# nltk
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import Stemmer # stemmer from pystemmer

# exports 
__all__ = ['userwarnings_words_extractor', 'UserWarningTf']

# note there could be pipes, to indicate different alternatives for the same parameters
parameters_pattern_escaped = re.compile(
r'''
    \\\{\\\{\\\{            # match \{\{\{
        (?P<options>        # named group options
            [^\{]*          # match anything but closed curly brakets
        )                   # end of the named group
    \\\}\\\}\\\}            # match \}\}\}
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

# pattern for nested substitution templates
subst_pattern_escaped = re.compile(
r'''
    \\\{\\\{                        # match \{\{
        (?:                         # begin of a non catching group
            \s                      # spaces or newlines
            |                       # or
            _                       # underscores
        )*                          # repeated 0 or multiple times
        subst:                      # match subst:
        (?P<pattern_name>           # begin of a named group called pattern_name 
            [^\{]*                  # match all except {
        )                           # close of the 
    \\\}\\\}                        # match \}\}
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

# match open and closed onlyinclude tags
onlyinclude_tag = re.compile(
r'''
    <                               # match <
        \s*                         # spaces multiple or 0 times
        (?:                         # begin of a non catching group
            \/                      # match /
            |                       # or nothing
        )                           # close the non cathing group
        onlyinclude                 # match onlyinclude
        \s*                         # spaces multiple or 0 times
    >                               # match >
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

# match open and closed includeonly tags
include_only_tag = re.compile(
r'''
    <                               # match <
        \s*                         # spaces multiple or 0 times
        (?:                         # begin of a non catching group
            \/                      # match /
            |                       # or nothing
        )                           # close the non cathing group
        includeonly                 # match includeonly
        \s*                         # spaces multiple or 0 times
    >                               # match >
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

def userwarnings_words_extractor(text: str, language: str) -> UserWarningTf:
    """Extract some information like a list of word stemmed in that particular text"""
    # wikicode
    wikicode = mwparserfromhell.parse(text)
    # remove the noinclude elements
    wikicode = remove_no_include(wikicode)
    # keep onlyinclude if present
    wikicode = keep_only_includes(wikicode)
    # keep or remove the include_only tags
    wikicode = keep_or_include_include_only(wikicode)
    # clean the wikicode
    wikicode = clean_string(str(wikicode))
    # remove stop words
    wikicode = remove_stop_words(wikicode, language)
    # NOTE: no streamming for now. words
    # wikicode = stream_words(wikicode, language)
    # count the occurences of each word
    words = word_tokenize(wikicode)
    # words dictionary
    words_dict = dict()
    # count the words
    for w in words:
        if not w in words_dict:
            words_dict[w] = 1
        else:
            words_dict[w] += 1
    return UserWarningTf(wikicode, words_dict, len(words))

def remove_stop_words(text: str, language: str) -> str:
    """Removes the stopwords"""
    return ' '.join(list(word for word in word_tokenize(text) if not word in stopwords.words(language)))

def stream_words(text: str, language: str) -> str:
    # stremmer
    stemmer = Stemmer.Stemmer(language)
    return ' '.join(list(map(stemmer.stemWord, word_tokenize(text))))

def clean_string(text: str) -> str:
    """Clean the string, keeps everything but words"""
    return re.sub(r'[^\w]', ' ', text)

def remove_no_include(wikicode: mwparserfromhell.wikicode.Wikicode) -> mwparserfromhell.wikicode.Wikicode:
    """Removes the noinclude tags"""
    for tag in wikicode.filter_tags():
        if tag.tag.matches('noinclude'):
            try:
                wikicode.remove(tag)
            except ValueError:
                pass
    return wikicode

def keep_only_includes(wikicode: mwparserfromhell.wikicode.Wikicode) -> mwparserfromhell.wikicode.Wikicode:
    """Keeps only the onlyincludes tags if any"""
    only_include_present = False
    to_remove = list()
    for tag in wikicode.filter_tags(recursive=False):   # select only the most external one
        if tag.tag.matches('onlyinclude'):
            only_include_present = True
        else:
            to_remove.append(tag)
    if only_include_present:
        for tag in to_remove:
            try:
                wikicode.remove(tag)
            except ValueError:
                pass
    wikicode =  mwparserfromhell.parse(re.sub(onlyinclude_tag, '', str(wikicode)))
    return wikicode

def keep_or_include_include_only(wikicode: mwparserfromhell.wikicode.Wikicode) -> mwparserfromhell.wikicode.Wikicode:
    """
    If there is an onlyinclude tag, the function removes the includeonly tags but not the content of them (remove_tags set o true)
    If there are no onlyinclude tags (remove_tags set to false) then it keeps the content of the includeonly tags
    """
    wikicode = mwparserfromhell.parse(re.sub(include_only_tag, '', str(wikicode)))
    return wikicode