"""
TEMPLATES:
https://en.wikipedia.org/wiki/Help:Template
https://it.wikipedia.org/wiki/Aiuto:Template
https://it.wikipedia.org/wiki/Aiuto:Subst
https://it.wikipedia.org/wiki/Aiuto:Subst
"""

import regex as re
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional, Mapping
from .common import CaptureResult, Identifier, Span
from .types.user_warning_template import UserWarningTemplate

# exports 
__all__ = ['userwarnings_regex_extractor', 'UserWarningTemplate']

# note there could be pipes, to indicate different alternatives for the same parameters
parameters_pattern_escaped = re.compile(
r'''
    \\\{\\\{\\\{            # match \{\{\{
        (?P<options>        # named group options
            [^{]*           # match anything but closed curly brakets
        )                   # end of the named group
    \\\}\\\}\\\}            # match \}\}\}
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

# TODO see what happens if there are multiple <includeonly> or <onlyinclude>

def userwarnings_regex_extractor(text: str) -> str:
    # list of parameters
    parameters = set()

    # remove the noinclude elements
    # TODO inefficient, but the Xml will always be not well formatted, lxml and Beautiful Soup don't parse it right
    text, found = xml_tag_content(text, 'noinclude', False)

    # TODO inefficient, but the Xml will always be not well formatted, lxml and Beautiful Soup don't parse it right
    text, found = xml_tag_content(text, 'onlyinclude', True)    # keep the onlyinclude
    
    if found:   # if found the onlyinclude
        # the includeonly are seen inside, so the labels <includeonly> should be deleted
        text = text.replace('<includeonly>', '')
        text = text.replace('</includeonly>', '')
        # we do not care about the representation, but only about the template that will be transcluded or substituted
    else:
        # keep the includeonly if exists, same TODO, for now concatenated
        # TODO inefficient, but the Xml will always be not well formatted, lxml and Beautiful Soup don't parse it right
        text, found = xml_tag_content(text, 'includeonly', True)

    # TODO what happens if tags are nested?

    # regex escape
    text = re.escape(text.strip())  # why the escape does not work well
    text = text.replace('/', '\/')
    to_subst = list()   # what to substitute from text

    # NOTE indentification of variables
    for match in parameters_pattern_escaped.finditer(text): # returns an iterator of match object
        # TODO check what happens if multiple onlyinclude, for now, concatenated
        if check_options_presence(match):            # extract a named group called options (name of the wikipause template used)
            original_text = match.group('options')
            adjusted_options = original_text
            options = original_text.split('|')
            # remember to substitute
            adjusted_options = '(?:'    # add the uncatching group
            for opt in options:
                if opt:
                    # sanification
                    if opt[-1] == '\\':
                        opt = opt[:-1]
                    # save the parameter
                    parameters.add(opt)
                    adjusted_options = ''.join([adjusted_options, '\{\{\{%s\}\}\}|{%s}'%(opt, opt)])    # add the options and the {} with the paramter name, so it could be substituted
                else:
                    # add an empty one
                    adjusted_options = ''.join([adjusted_options, '|'])
            adjusted_options = ''.join([adjusted_options, ')']) # close the group
            to_subst.append({'start': match.start(), 'end': match.end(), 'string': adjusted_options})
        
    for el in reversed(to_subst):
        text = text[0: el['start']] + el['string'] + text[el['end'] : ]

    return UserWarningTemplate(text, list(parameters))

def check_options_presence(match: Iterator[re.Match]) -> bool:
    """Checks if some groups is present inside the match object"""
    try:
        match.group('options')
        return True
    except IndexError:
        return False

def xml_tag_content(text: str, tag_name: str, include: bool) -> [str, bool]:
    found_tag = False
    while tag_name in text:
        match_open_index = re.search('<{}>'.format(tag_name), text)
        match_close_index = re.search('</{}>'.format(tag_name), text)
        if match_open_index and match_close_index:
            if include:
                match_open_index = match_open_index.end()
                match_close_index = match_close_index.start()
            else:
                match_open_index = match_open_index.start()
                match_close_index = match_close_index.end()
            if len(text) > match_close_index:
                text = text[0 : match_open_index :] + text[match_close_index : :]
                found_tag = True
        else:
            break
    return text, found_tag