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
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional, Mapping
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
        %s                  # match the field name
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
    re.compile(wikibreak_field_pattern%(field_name.lower()), re.IGNORECASE | re.UNICODE | re.VERBOSE | re.MULTILINE) 
    for field_name in wikibreaks.wikibreak_named_fields
]

# TODO MAKE IT BETTER
def wikibreaks_extractor(text: str) -> Iterator[CaptureResult[Wikibreak]]:
    for pattern in WIKIBREAKS_REs:
        for match in pattern.finditer(text): # returns an iterator of match object
            if check_wikibreaks_presence(match): # extract a named group called lang (basically it contains a single language if it's the user's mother tongue, otherwise lang-level)
                wiki_name = match.group('type')
                
                if not wiki_name:
                    write_error(pattern, match)
                    return
                
                wikipause_obj = Wikibreak(wiki_name, '', '', '', '', list())
                wikipause_dict = dict()
                wikipause_dict['not_parsed'] = list()
                
                # Parse the options if any
                if check_options(match):

                    # parse the options
                    parsed_options = list(
                        match.group('options').strip().replace('_', '') .split('|') # retrieve the languages I am interested in for the user, 
                        # remove spaces, remove _ which count as spaces and split for parameters)
                    )

                    positional_counter = 1  # counter for positional arguments

                    for opt in parsed_options:  # Ok to substitute parameters

                        # extract a known field + value couple if any
                        named_field = wikibreaks_fields_extractor(opt.strip())
                        if named_field:
                            if named_field[0] in wikibreaks.wikibreak_fields_to_wikipause_obj_field:
                                # map the value in the dictionary
                                wikipause_dict[
                                    wikibreaks.wikibreak_fields_to_wikipause_obj_field[
                                        named_field[0]
                                    ]
                                ] = named_field[1]
                            else:
                                # not recognized
                                wikipause_dict['not_parsed'].append(opt)
                        else:
                            # There are two cases:
                            # 1) It is a positional argument
                            # 2) Not recognized by the list of parameters

                            # case 2
                            if '=' in opt and len(opt) > 0:
                                # Not recognized
                                wikipause_dict['not_parsed'].append(opt)

                            # case 1
                            if len(opt) > 0:
                                if str(positional_counter) in wikibreaks.wikibreak_fields_to_wikipause_obj_field:
                                    wikipause_dict[
                                        wikibreaks.wikibreak_fields_to_wikipause_obj_field[
                                            str(positional_counter)
                                        ]
                                    ] = opt
                                else:
                                    wikipause_dict['not_parsed'].append(opt)
                        positional_counter += 1
                    
                    # generate the object from the dictionary
                    wikipause_obj.from_dict(wikipause_dict)
                else:
                    pass

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

def check_options(match) -> bool:
    """Checks if some groups is present inside the match object"""
    try:
        match.group('options')
        return True
    except IndexError:
        return False

def check_wikibreaks_presence(match) -> bool:
    """Checks if some groups is present inside the match object"""
    try:
        match.group('type')
        return True
    except IndexError:
        return False

def check_wikibreaks_fields_presence(match) -> bool:
    """Checks if some groups is present inside the match object"""
    try:
        match.group('field')
        match.group('value')
        return True
    except IndexError:
        return False
