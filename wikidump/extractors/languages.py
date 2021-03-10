"""Extractor for "languages" known by Wikipedians in their personal page https://en.wikipedia.org/wiki/Wikipedia:Babel. 

Common example of Wikipedia:Babel template: {{Babel|zh|es-4|ru-2}}

Please not there is also this extension of Babel that should be considered: https://www.mediawiki.org/wiki/Extension:Babel#Usage

And what's so called Babel-N template: :{{Babel-5|ca|es-3|en-2|fr-2|de-1}}

There are also some alternatives to the Babel template:
    - standalone language templates. Format: {{User xx-1}}{{User yy-1}}{{User zz-1}}. https://en.wikipedia.org/wiki/Category:Language_user_templates
    - Babel-N template. Format: {{Babel-N|1={{User xx-1}}{{User yy-1}}{{User zz-1}}}} https://en.wikipedia.org/wiki/Template:Babel-N
    - top and bottom templates to make the box. Format: {{Userboxtop}}{{User xx-1}}{{User yy-1}}{{User zz-1}}{{Userboxbottom}}. https://en.wikipedia.org/wiki/Template:Userboxtop https://en.wikipedia.org/wiki/Template:Userboxbottom
    - Babel extension. Format: {{#Babel:xx|yy-1|zz-2}}  # https://www.mediawiki.org/wiki/Extension:Babel#Usage
"""

import regex as re
from typing import Iterator

from .common import CaptureResult, Identifier, Span

class LanguageLevel:
    """Class which stores the language and the level associatecd with the user"""


    """Map n value (mother tongue language level) into 6 (greater than each possibile value into Babel teamplate)"""
    MOTHER_TONGUE_LEVEL = 6

    """The pair language name and level of knowledge"""
    def __init__(self, lang: str, level: int):
        self.lang = lang.strip().lower()
        self.level = level

    def __lt__(self, other):
        if self.lang == other.lang:
            return self.level < other.level
        return self.lang < other.lang

    def __eq__(self, other):
        return self.lang == other.lang and self.level == other.level

    def __repr__(self):
        return 'lang: {}; level: {}'.format(self.lang, self.level)

__all__ = ['language_knowledge', 'LanguageLevel', ]

babel_standard_pattern = r'{{(?:\s|\_)*Babel(?:\s|\_)*(?:(?P<lang>(\|((?:\s|\_)*(?:[a-zA-Z]{2}|[a-zA-Z]{3})(\-(?:0|1|2|3|4|5|n)|)|)(?:\s|\_)*)+)|(.*?(?:{{!}}|{{=}|).*?)*)}}' # TODO test and clean
babel_extension_template = r'{{\s*#babel:(?:(?P<first_lang>((?:\s|\_)*(?:[a-zA-Z]{2}|[a-zA-Z]{3}))(\-(?:0|1|2|3|4|5|n)|)|)|(?:\s|\_)*(?P<lang>(\|((?:\s|\_)*(?:[a-zA-Z]{2}|[a-zA-Z]{3})(\-(?:0|1|2|3|4|5|n)|)|)(?:\s|\_)*)*)|(.*?(?:{{!}}|{{=}|).*?)*)}}' # TODO check if this can be incorporate into the first
user_template_format = r'{{(?:\s|\_)*User(?:\s|\_)*(?P<lang>(?:[a-zA-Z]{2}|[a-zA-Z]{3})(\-(?:0|1|2|3|4|5|n)|))}}'
babel_n_template = r'{{(?:\s|\_)*Babel\-\d(?:\s|\_)*(?:(?P<lang>(\|((?:\s|\_)*(?:[a-zA-Z]{2}|[a-zA-Z]{3})(\-(?:0|1|2|3|4|5|n)|)|)(?:\s|\_)*)+)|(.*?(?:{{!}}|{{=}|).*?)*)}}' # TODO, there are many varaints, this is the most used one at least in the catalan wiki
userboxes_template = r'' # TODO define, it seemed to be contained in the user_template format

KNOWN_LANGUAGES_REs = [
    re.compile(babel_standard_pattern, re.I | re.U),
    re.compile(babel_extension_template, re.I | re.U),
    re.compile(user_template_format, re.I | re.U),
    re.compile(babel_n_template, re.I | re.U),
    # re.compile(userboxes_template, re.I | re.U)
]

def language_knowledge(text: str) -> Iterator[CaptureResult[LanguageLevel]]:
    for pattern in KNOWN_LANGUAGES_REs:
        for match in pattern.finditer(text): # returns an iterator of match object
            if check_language_presence(match): # extract a named group called lang (basically it contains a single language if it's the user's mother tongue, otherwise lang-level)
                raw_langs = retrieve_group(match)
                if not raw_langs:
                    write_error(pattern, match)
                    return
                # Need to parse the languages
                parsed_languages = list(filter(None, raw_langs.strip().split('|'))) # retrieve the languages I am interested in for the user
                for langs in parsed_languages:
                    # sample templates it-4
                    l = langs.split('-', 1)
                    if len(l) > 1:
                        if l[1].lower() == 'n':
                            l[1] = LanguageLevel.MOTHER_TONGUE_LEVEL
                        lang_knowedge = LanguageLevel(l[0], int(l[1]))
                    else:
                        lang_knowedge = LanguageLevel(l[0], LanguageLevel.MOTHER_TONGUE_LEVEL)
                    
                    # TODO filter the match with some languages retrieved from https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

                    yield CaptureResult(
                        data=(lang_knowedge), span=(match.start(), match.end())
                    )
            else:
                pass  # TODO what to do if there isn't any match with lang group

def write_error(pattern re.Pattern, match: Iterator[re.Match]) -> None:
    with open('error.txt', 'a+') as f:
        f.write('patter who failed {} match {}\n'.format(pattern, match))

def check_language_presence(match: Iterator[re.Match]) -> bool:
    """Checks if some group is present inside the """
    try:
        match.group('lang') or match.group('first_lang')
        return True
    except IndexError:
        return False

def retrieve_group(match: Iterator[re.Match]) -> str:
    """Retrieve the right group according to the position of the language"""
    try:
        raw_langs = match.group('first_lang')
    except IndexError:
        raw_langs = match.group('lang')
    return raw_langs