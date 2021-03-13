"""
WIKIBREAKS DOCUMENTATION
There are many wikibreaks templates as I can see:
https://en.wikipedia.org/wiki/Template:Wikibreak:
# Basics attributes I need to scrape
{{wikibreak | [Name] | back = | type = | message  = | align = | image = | noimage = | imagesize = | spacetype = | style = }}
# to consider {{in-house switch}} {{At school}} {{Exams}} {{Vacation}} {{Out of town}} {{Personal issues}}
"""

import regex as re
from .. import wikibreaks
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional
from .common import CaptureResult, Identifier, Span
from .types.wikibreak import Wikibreak
from .utils.language_utils_functions import (
    write_error,
    write_error_level_not_recognized,
    is_level
)

# exports 
__all__ = ['wikibreaks_extractor', 'Wikibreak', ]

### Without any named parameter:
#{{ wikipause | ciao  |    come      |    long                 }}
#    type       user       when back      dunno why displayed

# https://regex101.com/r/BK0q6s/1
wikibreak_pattern = r'''
    \{\{                    # match {{
        (?:                 # non-capturing group
            \s              # match any spaces
            |               # or
            \_              # match underscore (count as space)
        )*                  # match 0 or multiple times
        (?P<type>           # namedgroup named type
            %s              # wikibreak word to substitute
        )                   # closed named group
        (?:                 # start of a non capturing group
            \s              # match any spaces
            |               # or
            \_              # match _
        )*                  # repeat the group 0 or n times
        \|                  # match pipe
        (?P<options>        # named group options
            [^{]*           # match anything but closed curly brakets
        )                   # end of the named group
    \}\}'''                 # match }}

# https://regex101.com/r/Cuey3K/1
wikibreak_empty_pattern = r'''
    \{\{                    # match {{
        (?:                 # non-capturing group
            \s              # match any spaces
            |               # or
            \_              # match underscore (count as space)
        )*                  # match 0 or multiple times
        (?P<type>           # named group named type
            %s              # wikibreak word to substitute
        )                   # closed named group
        (?P<options>        # named group named options
            (?:             # non-capturing group
                \s          # match any spaces
                |           # or
                \_          # match _
            )*              # repeat the group 0 or n times
        )                   # end of a non captuiring group
    \}\}'''                 # match }}


# https://regex101.com/r/0jdhle/1
wikibreak_field_pattern = r'''
    ^                       # start of the string
    (?:                     # start of the non capturing group
        \s*                 # match any spaces
    )                       # end of the non capturing group
    (?P<field>              # field named group
        break               # match break
    )                       # end of the named group
    (?:                     # start of the non capturing group
        \s*                 # match any spaces
    )                       # close the non capturing group
    =                       # match =
    (?P<value>              # begin of the value named group
        (?:                 # begin of an non capturing group
            .               # match anything but \n
        |                   # or
            \n              # newline
        )*                  # repeat the non capturing group 0 or n times
    )                       # end of the named group
    $                       # end of the string
'''

WIKIBREAKS_PATTERN_REs = [ 
    re.compile(wikibreak_pattern%(w_word.lower()), re.IGNORECASE | re.UNICODE | re.VERBOSE | re.MULTILINE) 
    for w_word in wikibreaks.wikibreak_standard_words
]

WIKIBREAKS_EMPTY_PATTERN_REs = [
    re.compile(wikibreak_empty_pattern%(w_word.lower()), re.IGNORECASE | re.UNICODE | re.VERBOSE | re.MULTILINE) 
    for w_word in wikibreaks.wikibreak_standard_words
]

WIKIBREAKS_REs = WIKIBREAKS_PATTERN_REs + WIKIBREAKS_EMPTY_PATTERN_REs

WIKIBREAKS_NAMED_FIELDS_REs = [
    # TODO
]

def wikibreaks_extractor(text: str) -> Iterator[CaptureResult[Wikibreak]]:
    for pattern in WIKIBREAKS_REs:
        for match in pattern.finditer(text): # returns an iterator of match object
            if check_wikibreaks_presence(match): # extract a named group called lang (basically it contains a single language if it's the user's mother tongue, otherwise lang-level)
                wiki_name = match.group('type')
                if not wiki_name:
                    write_error(pattern, match)
                    return
                wikipause_obj = Wikibreak(wiki_name, None, None, None, None)
                wikipause_dict = dict()
                # Parse the options if any
                if check_options(match):
                    parsed_options = list(filter(None, 
                        match.group('options').strip().replace('_', '') .split('|') # retrieve the languages I am interested in for the user, 
                        # remove spaces, remove _ which count as spaces and split for parameters)
                    ))
                    positional_counter = 0
                    for opt in parsed_options:  # Ok to substitute parameters
                        named_field = wikibreaks_fields_extractor(opt)
                        # TODO check if crashes if break= is given
                        # TODO mapping to define
                        if named_field:
                            if check_if_numbered_args(named_field[0]):
                                named_field[0] = int(named_field[0])
                            wikipause_dict[mapping[named_field[0]]] = named_field[1]
                        else:
                            # deve essere contato come un parametro posizionale, al massimo fino a 3 posizioni
                            # TODO mapping 2 to define -> maps index to field
                            field = opt.split('=', 1)[0]
                            if len(field) > 0:
                                wikipause_dict[mapping_2[positional_counter]] = field
                            else:
                                wikipause_dict[mapping_2[positional_counter]] = None
                        positional_counter += 1
                    # TODO generate the wikipause_obj from the wikipause_dict
                else:
                    pass
                # Should generate the wikipause object
                # search for a pattern in fields 
                yield CaptureResult(
                    data=(wikipause_obj), span=(match.start(), match.end())
                )
            else:
                pass

def wikibreaks_fields_extractor(text: str) -> Optional[Iterable[str]]: # TODO return smth
    for pattern in WIKIBREAKS_NAMED_FIELDS_REs:
        for match in pattern.finditer(text):
            if check_wikibreaks_fields_presence(match):
                field_name = match.group('field')
                field_value = match.group('value')
                if not field_name or not field_value:
                    write_error(pattern, match)
                    return
                return (field_name, field_value)
    return None

def check_if_numbered_args(text: str) -> bool:
    """Checks the argument text is castable as a number"""
    try:
        int(text)
        return True
    except IndexError:
        return False

def check_options(match: Iterator[re.Match]) -> bool:
    """Checks if some groups is present inside the match object"""
    try:
        match.group('options')
        return True
    except IndexError:
        return False

def check_wikibreaks_presence(match: Iterator[re.Match]) -> bool:
    """Checks if some groups is present inside the match object"""
    try:
        match.group('type')
        return True
    except IndexError:
        return False

def check_wikibreaks_fields_presence(match: Iterator[re.Match]) -> bool:
    """Checks if some groups is present inside the match object"""
    try:
        match.group('field')
        match.group('value')
        return True
    except IndexError:
        return False
