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

babel_standard_pattern = r'{{(?:\s|\_)*{Babel}[^\-](?:\s|\_)*(?P<lang>(.*?(?:{{!}}|{{=}}|).*?)*)}}'
babel_extension_template = r'{{\s*#{babel}:(?P<lang>(.*?(?:{{!}}|{{=}}|).*?)*)}}'
user_template_format = r'{{(?:\s|\_)*{User}(?:\s|\_)*(?P<lang>(?:[a-zA-Z]{{two}}|[a-zA-Z]{{three}})(\-(?:0|1|2|3|4|5|n)|))}}'
babel_n_template = r'{{(?:\s|\_)*{Babel}\-\d(?:\s|\_)*(?P<lang>(.*?(?:{{!}}|{{=}}|).*?)*)}}'

FORMATTED_STANDARD_BABEL_REs = [
    re.compile(babel_standard_pattern.format(Babel=b), re.I | re.U)
    for b in languages.babel_words
]

FORMATTED_EXTENSION_BABEL_REs = [
    re.compile(babel_extension_template.format(babel=b.lower()), re.I | re.U)
    for b in languages.babel_words
]

FORMATTED_N_BABEL_REs = [
    re.compile(babel_n_template.format(Babel=b), re.I | re.U)
    for b in languages.babel_words
]

FORMATTED_USER_TEMPLATE_REs = [
    re.compile(user_template_format.format(User=u, two='2', three='3'), re.I | re.U)
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
                parsed_languages = list(filter(None, raw_langs.strip().split('|'))) # retrieve the languages I am interested in for the user
                for langs in parsed_languages:
                    l = langs.split('-', 1)
                    if len(l) > 1:
                        if not is_level(l[1]):
                            write_error_level_not_recognized(match, l[1])
                            return
                        level = get_level(l[1])
                    else:
                        level = LanguageLevel.MOTHER_TONGUE_LEVEL
                    
                    if l[0] in languages.iso639_languages:
                        lang_knowedge = LanguageLevel(languages.iso639_languages[l[0]], level)
                        yield CaptureResult(
                            data=(lang_knowedge), span=(match.start(), match.end())
                        )
                    else:
                        write_error(pattern, match) # Language not recognized
            else:
                pass

def check_language_presence(match: Iterator[re.Match]) -> bool:
    """Checks if some group is present inside the match object"""
    try:
        match.group('lang')
        return True
    except IndexError:
        return False
