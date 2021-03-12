"""
WIKIBREAKS DOCUMENTATION
There are many wikibreaks templates as I can see:
https://en.wikipedia.org/wiki/Template:Wikibreak:
# Basics attributes I need to scrape
{{wikibreak | [Name] | back = | type = | message  = | align = | image = | noimage = | imagesize = | spacetype = | style = }}
# to consider {{in-house switch}} {{At school}} {{Exams}} {{Vacation}} {{Out of town}} {{Personal issues}}
"""

import regex as re
from typing import Iterator
from .. import wikibreaks
from .common import CaptureResult, Identifier, Span
from .types.wikibreak import Wikibreak
from .utils.language_utils_functions import (
    write_error,
    write_error_level_not_recognized,
    is_level
)

# TODO find a way to recognize the positional paramters, not only the named one
new = r'{{(?:\s|\_)*(?P<wikipause_name>wikibreak)(?:\s|\_)*(?:\|(?:(?P<name>(\s|\_)*[^\|}{=]+(?:\s|\_)*)|\||)}}'

# exports 
__all__ = ['wikibreaks_extractor', 'Wikibreak', ]

# Maybe type could be useful, let's see
wikibreak_pattern = r'{{(?:\s|\_)*(?P<type>{wikibreak})(?:\s|\_|\|\=|.*?)}}'

WIKIBREAKS_REs = [ 
    re.compile(wikibreak_pattern.format(wikibreak=w_word.lower()), re.I | re.U) 
    for w_word in wikibreaks.wikibreak_standard_words
]

def wikibreaks_extractor(text: str) -> Iterator[CaptureResult[Wikibreak]]:
    for pattern in WIKIBREAKS_REs:
        for match in pattern.finditer(text): # returns an iterator of match object
            if check_wikibreaks_presence(match): # extract a named group called lang (basically it contains a single language if it's the user's mother tongue, otherwise lang-level)
                wiki_name = match.group('type')
                if not wiki_name:
                    write_error(pattern, match)
                    return
                # Should generate the wikipause object
                # TODO parse the attributes
                wikipause_obj = Wikibreak(wiki_name, None, None, None, None)
                yield CaptureResult(
                    data=(wikipause_obj), span=(match.start(), match.end())
                )
            else:
                pass

def check_wikibreaks_presence(match: Iterator[re.Match]) -> bool:
    """Checks if some groups is present inside the match object"""
    try:
        match.group('type')
        return True
    except IndexError:
        return False
