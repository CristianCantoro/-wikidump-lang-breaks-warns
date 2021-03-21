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
            \/
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
            \/
            |
        )
        includeonly
        \s*
    >
''', re.UNICODE | re.VERBOSE | re.MULTILINE)

# TODO there could also be a chain of substitution

"""
https://en.wikipedia.org/w/index.php?title=Template:Template_sandbox&action=edit
https://en.wikipedia.org/w/index.php?title=Draft:Sandbox&action=edit

<onlyinclude>This is a sample template</onlyinclude>
<onlyinclude><includeonly>This is a sample template</includeonly> part 2</onlyinclude>
<includeonly>Hi there</includeonly>

Output: This is a sample template This is a sample template part 2 -> so as the wiki said the includeonly outside the onlyinclude will be ignored
Also, the onlyinclude will be concatenated if there are multiple
Test: passed

<includeonly>This is a sample template</includeonly>
<includeonly><includeonly>This is a sample template</includeonly> part 2</includeonly>
<includeonly>Hi there</includeonly>

Output: This is a sample template This is a sample template part 2 Hi there 
Also, the includeonly will be concatenated if there are multiple
Test: passed

<includeonly>This is a sample template</includeonly>
<includeonly><noinclude>This is a sample template</noinclude> part 2</includeonly>
<includeonly>Hi there</includeonly>

Output:
This is a sample template part 2 Hi there
Test: passed

So, as imagined the noinclude is not considered
"""

# TODO fix spaces problem:
# a possibile solution, to match strip the string and substitute \n with spaces?
# strip is basically needed because the html.parser changes the tags -> <br \> -> <br\>

# this produces: https://regex101.com/r/CTu4as/1
def userwarnings_regex_extractor(text: str) -> str:
    # list of parameters
    parameters = set()
    # templates which could be substituted
    sub_templates = set()
    document = BeautifulSoup(text, 'html.parser')
    # remove the noinclude elements
    remove_no_include(document)
    # keep onlyinclude if present
    document, only_include_present = keep_only_includes(document)
    # keep or remove the include_only tags
    document = keep_or_include_include_only(document, only_include_present)
    # regex escape
    document = regex_escape_document_text(document)

    to_subst = list()   # what to substitute from the document text
    option_counter = 0  # option counter
    # Options identification
    for match in parameters_pattern_escaped.finditer(document): # returns an iterator of match object
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
        document = document[0: el['start']] + el['string'] + document[el['end'] : ]

    # look for chain substitution
    for match in subst_pattern_escaped.finditer(document):
        sub_templates.add(match.group('pattern_name'))
    
    with open('template_to_retrieve.txt', 'a+') as f:
        f.write('{}\n'.format(sub_templates))

    return UserWarningTemplate(document, list(parameters), list(sub_templates))

def regex_escape_document_text(document: BeautifulSoup) -> str:
    """String to regex"""
    document = str(document)
    document = re.sub(' +', ' ', document).strip()
    document = re.escape(document)
    document = document.replace('/', r'\/')
    return document

def keep_or_include_include_only(document: BeautifulSoup, remove_tags: bool) -> BeautifulSoup:
    """
    If there is an onlyinclude tag then it removes the inludehonly tags but not the content of them
    If there are none onlyinclude tags then it keeps only the content of the includeonly tags
    """
    include_only = document.find_all('includeonly', recursive=False)
    new_text = ''
    if remove_tags:
        new_text = re.sub(include_only_tag, '', str(document))
    else:
        if include_only:
            for i_o in include_only:
                new_text = ' '.join(
                    [
                        new_text, 
                        re.sub(
                            include_only_tag,
                            '',
                            str(i_o)
                        )
                    ]
                )
    if new_text:
        document = BeautifulSoup(new_text, 'html.parser')
    return document

def keep_only_includes(document: BeautifulSoup) -> [BeautifulSoup, bool]:
    """Keeps only the onlyincludes tags if any"""
    only_includes = document.find_all('onlyinclude', recursive=False)
    only_include_present = False    # if onlyincludes are contained in the document
    if only_includes:
        new_text = ''
        for o_i in only_includes:
            new_text = ' '.join(
                [
                    new_text, 
                    re.sub(
                        onlyinclude_tag,
                        '',
                        str(o_i)
                    )
                ]
            )
        document = BeautifulSoup(new_text, 'html.parser')
        only_include_present = True
    return document, only_include_present

def remove_no_include(document: BeautifulSoup) -> None:
    """Removes the noinclude tags"""
    no_includes = document.find_all('noinclude')
    for n_i in no_includes:
        n_i.replace_with('')

def check_options_presence(match: Iterator[re.Match]) -> bool:
    """Checks if some groups is present inside the match object"""
    try:
        match.group('options')
        return True
    except IndexError:
        return False