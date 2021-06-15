"""
TEMPLATES:
https://en.wikipedia.org/wiki/Help:Template
https://it.wikipedia.org/wiki/Aiuto:Template
https://it.wikipedia.org/wiki/Aiuto:Subst
https://it.wikipedia.org/wiki/Aiuto:Subst
"""

import regex as re
from typing import Iterator
from .types.user_warning_template import UserWarningTemplate
import mwparserfromhell

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

# this produces: https://regex101.com/r/CoSTLw/1
def userwarnings_regex_extractor(text: str) -> str:
    # list of parameters
    parameters = set()
    # templates which could be substituted
    sub_templates = set()
    # prova
    wikicode = mwparserfromhell.parse(text)
    # remove the noinclude elements
    wikicode = remove_no_include(wikicode)
    # keep onlyinclude if present
    wikicode = keep_only_includes(wikicode)
    # keep or remove the include_only tags
    wikicode = keep_or_include_include_only(wikicode)
    # regex escape
    wikicode = regex_escape_text(str(wikicode))
    to_subst = list()   # what to substitute from the document text
    option_counter = 0  # option counter
    # Options identification todo see if it can be modified with the parser from hell
    for match in parameters_pattern_escaped.finditer(wikicode): # returns an iterator of match object
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

    # perform the parameter substitution
    while to_subst:
        el = to_subst.pop()
        wikicode = wikicode[0: el['start']] + el['string'] + wikicode[el['end'] : ]

    # look for chain substitution
    for match in subst_pattern_escaped.finditer(wikicode):
        sub_templates.add(match.group('pattern_name'))
    
    # save the templates to retrieve
    with open('template_to_retrieve.txt', 'a+') as f:
        f.write('{}\n'.format(sub_templates))

    # adjust spaces in regex
    wikicode = re.sub(r'\\\s', r'(?:\s|)', wikicode)

    return UserWarningTemplate(wikicode, list(parameters), list(sub_templates))

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

def regex_escape_text(text: str) -> str:
    """String to regex"""
    document = re.escape(text)
    document = document.replace('/', r'\/')
    return document

def check_options_presence(match: Iterator[re.Match]) -> bool:
    """Checks if some groups is present inside the match object"""
    try:
        match.group('options')
        return True
    except IndexError:
        return False