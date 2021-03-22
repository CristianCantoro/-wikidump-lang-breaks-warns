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
# Beautiful soup
from bs4 import BeautifulSoup

# exports 
__all__ = ['userwarnings_regex_extractor', 'UserWarningTemplate']

# note there could be pipes, to indicate different alternatives for the same parameters
parameters_pattern_escaped = re.compile(
r'''
    \\\{\\\{\\\{            # match \{\{\{
        (?P<options>        # named group options
            [^\{]*          # match anything but closed curly brakets
        )                   # end of the named group
    \\\}\\\}\\\}            # match \}\}\}
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

subst_pattern_escaped = re.compile(
r'''
    \\\{\\\{
        (?:
            \s
            |
            _
        )*
        subst:
        (?P<pattern_name>
            [^\{]*
        )
    \\\}\\\}
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

onlyinclude_tag = re.compile(
r'''
    <
        \s*
        (?:
            \\\/
            |
        )
        onlyinclude
        \s*
    >
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

include_only_tag = re.compile(
r'''
    <
        \s*
        (?:
            \\\/
            |
        )
        includeonly
        \s*
    >
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

noinclude_pattern_lazy = re.compile(
    r'''
    <
        \s*
        noinclude
        \s*
    >
    (?:
        \s
        |
        .
    )*?
    <
        \s*
        \\\/
        noinclude
        \s*
    >
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

includeonly_pattern_lazy = re.compile(
    r'''
    <
        \s*
        includeonly
        \s*
    >
    (?:
        \s
        |
        .
    )*?
    <
        \s*
        \\\/
        includeonly
        \s*
    >
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

onlyinclude_pattern_lazy = re.compile(
    r'''
    <
        \s*
        onlyinclude
        \s*
    >
    (?:
        \s
        |
        .
    )*?
    <
        \s*
        \\\/
        onlyinclude
        \s*
    >
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

|| w ||2

# TODO there could also be a chain of substitution

"""
https://en.wikipedia.org/w/index.php?title=Template:Template_sandbox&action=edit
https://en.wikipedia.org/w/index.php?title=Draft:Sandbox&action=edit

<onlyinclude>This is a sample template</onlyinclude>
<onlyinclude><includeonly>This is a sample template</includeonly> part 2</onlyinclude>
<includeonly>Hi there</includeonly>

Output: This is a sample templateThis is a sample template part 2 -> so as the wiki said the includeonly outside the onlyinclude will be ignored
Also, the onlyinclude will be concatenated if there are multiple
Test: passed

<includeonly>This is a sample template</includeonly>
<includeonly><includeonly>This is a sample template</includeonly> part 2</includeonly>
<includeonly>Hi there</includeonly>

Output: This is a sample template This is a sample template part 2 Hi there 
Also, the includeonly will be concatenated if there are multiple
Test: not passed: TODO think about what to do

<includeonly>This is a sample template</includeonly>
<includeonly><noinclude>This is a sample template</noinclude> part 2</includeonly>
<includeonly>Hi there</includeonly>

Output:
This is a sample template
 part 2
Hi there
Test: passed

So, as imagined the noinclude is not considered
"""

# this produces: https://regex101.com/r/VfQeDf/1
def userwarnings_regex_extractor(text: str) -> str:
    # list of parameters
    parameters = set()
    # templates which could be substituted
    sub_templates = set()
    # regex escape
    text = regex_escape_text(text)
    # remove the noinclude elements
    text = remove_no_include(text)
    # keep onlyinclude if present
    text, only_include_present = keep_only_includes(text)
    # keep or remove the include_only tags
    text = keep_or_include_include_only(text, only_include_present)
    to_subst = list()   # what to substitute from the document text
    option_counter = 0  # option counter
    # Options identification
    for match in parameters_pattern_escaped.finditer(text): # returns an iterator of match object
        if check_options_presence(match):            # extract a named group called options (name of the wikipause template used)
            options = match.group('options').split('|') # list of options
            # remember to substitute
            new_options = '(?P<{}>'.format('options_{}'.format(option_counter))    # add the catching group (option_number of option)
            first_opt = True
            for opt in options:
                if opt:
                    # sanification from the re.escape
                    if opt[-1] == '\\':
                        opt = opt[:-1]
                    # save the parameter
                    parameters.add(opt) # add the parameter as a possibile paramter to the template
                    if first_opt:
                        # add the options and the {} with the paramter name, so it could be substituted
                        # add the possibility to use whatever text the user wants
                        new_options = ''.join([new_options, r'\{\{\{%s\}\}\}|[^}]*'%(opt)])    
                        first_opt = False
                    else:
                        new_options = ''.join([new_options, r'|\{\{\{%s\}\}\}'%(opt)])
                else:
                    # add an empty parameter
                    new_options = ''.join([new_options, '|'])
            new_options = ''.join([new_options, ')']) # close the catching group
            # object to substitute
            to_subst.append({'start': match.start(), 'end': match.end(), 'string': new_options})
            option_counter += 1
    
    while to_subst:
        el = to_subst.pop()
        text = text[0: el['start']] + el['string'] + text[el['end'] : ]

    # look for chain substitution
    for match in subst_pattern_escaped.finditer(text):
        sub_templates.add(match.group('pattern_name'))
    
    with open('template_to_retrieve.txt', 'a+') as f:
        f.write('{}\n'.format(sub_templates))

    return UserWarningTemplate(text, list(parameters), list(sub_templates))

def remove_no_include(text: str) -> str:
    """Removes the noinclude tags"""
    return re.sub(noinclude_pattern_lazy, '', text)

def keep_only_includes(text: str) -> [str, bool]:
    only_includes = re.findall(onlyinclude_pattern_lazy, text)
    only_include_present = False
    if only_includes:
        new_text = ''
        for o_i in range(len(only_includes)):
            tags = re.findall(onlyinclude_tag, only_includes[o_i])
            new_text = r'\s*'.join([new_text, only_includes[o_i]])
            if len(tags) > 2: # another tag should be open but not closed
                # to avoid this cases:
                    # <onlyinclude><onlyinclude>This is a sample template</onlyinclude> part 2</onlyinclude>
                    # matched: <onlyinclude><onlyinclude>This is a sample template</onlyinclude>
                    # escluded: part 2</onlyinclude> -> with (?:\s|.)*? we basically include it in some way
                new_text = ''.join([new_text, r'(?:\s|.)*?'])
        new_text = re.sub(onlyinclude_tag, '', new_text)
        only_include_present = True
    else:
        new_text = text
    return new_text, only_include_present

def keep_or_include_include_only(text: str, remove_tags: bool) -> str:
    """
    If there is an onlyinclude tag, the function removes the inludeonly tags but not the content of them
    If there are none onlyinclude tags then it keeps only the content of the includeonly tags
    """
    include_only = re.findall(includeonly_pattern_lazy, text)
    if remove_tags:
        text = re.sub(include_only_tag, '', text)
    else:
        if include_only:
            text = ''
            for i_o in range(len(include_only)):
                tags = re.findall(include_only_tag, include_only[i_o])
                text = r'\s*'.join([text, include_only[i_o]])
                if len(tags) > 2: # another tag should be open but not closed
                    # to avoid this cases:
                        # <includeonly><includeonly>This is a sample template</includeonly> part 2</includeonly>
                        # matched: <includeonly><includeonly>This is a sample template</includeonly>
                        # escluded: part 2</includeonly> -> with (?:\s|.)*? we basically include it in some way
                    text = ''.join([text, r'(?:\s|.)*?'])
            text = re.sub(include_only_tag, '', text)
    return text

def regex_escape_text(text: str) -> str:
    """String to regex"""
    document = re.escape(text.strip())
    document = document.replace('/', r'\/')
    return document

def check_options_presence(match: Iterator[re.Match]) -> bool:
    """Checks if some groups is present inside the match object"""
    try:
        match.group('options')
        return True
    except IndexError:
        return False