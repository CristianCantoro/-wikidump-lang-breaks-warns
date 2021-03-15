"""Extractor for "languages" known by Wikipedians in their personal page https://en.wikipedia.org/wiki/Wikipedia:Babel. 
There are also some alternatives to the Babel template:
    - standalone language templates. Format: {{User xx-1}}{{User yy-1}}{{User zz-1}}. https://en.wikipedia.org/wiki/Category:Language_user_templates
    - Babel-N template. Format: {{Babel-N|1={{User xx-1}}{{User yy-1}}{{User zz-1}}}} https://en.wikipedia.org/wiki/Template:Babel-N
    - top and bottom templates to make the box. Format: {{Userboxtop}}{{User xx-1}}{{User yy-1}}{{User zz-1}}{{Userboxbottom}}. https://en.wikipedia.org/wiki/Template:Userboxtop https://en.wikipedia.org/wiki/Template:Userboxbottom
    - Babel extension. Format: {{#Babel:xx|yy-1|zz-2}}  # https://www.mediawiki.org/wiki/Extension:Babel#Usage
"""

import regex as re
from typing import Iterator
from .. import languages
from .common import CaptureResult, Identifier, Span
from .types.language_level import LanguageLevel
from .utils.language_utils_functions import (
    is_level, 
    get_level,
    write_error_level_not_recognized, 
    write_error
)

# exports 
__all__ = ['language_knowledge', 'LanguageLevel', ]

# https://regex101.com/r/B2iULI/1
babel_standard_pattern = r'''
    \{\{                        # match {{
        (?:                     # non-capturing group
            \s                  # match any spaces
            |                   # or
            \_                  # match underscore (count as space)
        )*                      # 0 or multiple time the non-capturing group
        %s                      # Babel word to replace
        [^\-]                   # not match a - , to esclude babel_standard_pattern from babel_n_template
        (?P<lang>               # named group <lang>
            [^{]*               # match anything but }, {{Babel | it | {{User en}} }} which are bad formatted are considered invalid
        )                       # end named group
    \}\}'''                     # match }}

# https://regex101.com/r/OoyliH/1
babel_extension_template = r'''
    \{\{                        # match {{
        (?:                     # non-capturing group
            \s                  # match any spaces
            |                   # or
            \_                  # match underscore (count as space)
        )*                      # 0 or multiple time the non-capturing group
        \#                      # 
        %s:                     # Babel word to replace
        (?P<lang>               # named group <lang>
            [^{]*               # match anything but }, {{Babel | it | {{User en}} }} which are bad formatted are considered invalid
        )                       # end named group
    \}\}'''                     # match }}

# https://regex101.com/r/bVNcOu/1
user_template_format = r'''
    \{\{                        # match {{
        (?:                     # non-capturing group
            \s                  # match any spaces
            |                   # or
            \_                  # match underscore (count as space)
        )*                      # 0 or multiple time the non-capturing group
        %s                      # User word
        (?:                     # non-capturing group
            \s                  # match any spaces
            |                   # or
            \_                  # match underscore (count as space)
        )*                      # 0 or multiple time the non-capturing group
        (?P<lang>               # named group <lang>
            (?:                 # non-capturing group
                [a-zA-Z]{2}     # any alphabetical character repeated 2 times
                |               # or
                [a-zA-Z]{3}     # any alphabetical character repeated 3 times
            )                   # close non capturing group
            (?:                 # begin non capturing group                      
                \-              # match -
                (?:             # begin non capturing group     
                    0
                    |
                    1
                    |
                    2
                    |
                    3
                    |
                    4
                    |
                    5
                    |
                    n           # mother tongue level
                )
                |               # or
                                # match none
            )
            (?:                 # non-capturing group
                \s              # match any spaces
                |               # or
                \_              # match underscore (count as space)
            )*                   
        )
    \}\}'''                     # match }}

# https://regex101.com/r/3z73BE/1
babel_n_template = r'''
    \{\{                        # match {{
        (?:                     # non-capturing group
            \s                  # match any spaces
            |                   # or
            \_                  # match underscore (count as space)
        )*                      # 0 or multiple time the non-capturing group
        %s                      # Babel word to replace
        \-                      # match -
        \d                      # match a single digit           
        (?P<lang>               # named group <lang>
            [^{]*               # match anything but }, {{Babel | it | {{User en}} }} which are bad formatted are considered invalid
        )                       # end of the non-capturing group
    \}\}'''                     # match }}

FORMATTED_STANDARD_BABEL_REs = [
    re.compile(babel_standard_pattern%(b.replace(' ', '\ ')), re.IGNORECASE | re.UNICODE | re.VERBOSE | re.MULTILINE)
    for b in languages.babel_words
]

FORMATTED_EXTENSION_BABEL_REs = [
    re.compile(babel_extension_template%(b.replace(' ', '\ ')), re.IGNORECASE | re.UNICODE | re.VERBOSE | re.MULTILINE)
    for b in languages.babel_words
]

FORMATTED_N_BABEL_REs = [
    re.compile(babel_n_template%(b.replace(' ', '\ ')), re.IGNORECASE | re.UNICODE | re.VERBOSE | re.MULTILINE)
    for b in languages.babel_words
]

FORMATTED_USER_TEMPLATE_REs = [
    re.compile(user_template_format%(u.replace(' ', '\ ')), re.IGNORECASE | re.UNICODE | re.VERBOSE | re.MULTILINE)
    for u in languages.user_words
]

KNOWN_LANGUAGES_REs = FORMATTED_STANDARD_BABEL_REs + FORMATTED_EXTENSION_BABEL_REs + FORMATTED_N_BABEL_REs + FORMATTED_USER_TEMPLATE_REs

def language_knowledge(text: str) -> Iterator[CaptureResult[LanguageLevel]]:
    for pattern in KNOWN_LANGUAGES_REs:
        for match in pattern.finditer(text): # returns an iterator of match object
            if check_language_presence(match): # extract a named group called lang (basically it contains a single language if it's the user's mother tongue, otherwise lang-level)
                raw_langs = match.group('lang')
                if not raw_langs:
                    write_error(pattern, match)
                    return
                parsed_languages = list(filter(None, 
                    raw_langs.strip().replace('_', '') .split('|') # retrieve the languages I am interested in for the user, 
                    # remove spaces, remove _ which count as spaces and split for parameters)
                )) 
                for langs in parsed_languages:
                    langs = langs.strip()
                    l = langs.split('-', 1) # retrieve the couple language - level, if any level specified
                    if len(l) > 1:
                        if not is_level(l[1]):
                            write_error_level_not_recognized(match, l[1])
                            return
                        level = get_level(l[1])
                    else:
                        level = LanguageLevel.MOTHER_TONGUE_LEVEL
                    
                    if l[0] in languages.iso639_languages:  # is an iso639 language
                        lang_knowedge = LanguageLevel(languages.iso639_languages[l[0]], level)
                        yield CaptureResult(
                            data=(lang_knowedge), span=(match.start(), match.end())
                        )
                    else:
                        write_error(pattern, match) # Language not recognized
            else:
                pass

def check_language_presence(match) -> bool:
    """Checks if some group is present inside the match object"""
    try:
        match.group('lang')
        return True
    except IndexError:
        return False
