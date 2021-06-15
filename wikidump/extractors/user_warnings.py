import regex as re
from .. import user_warnings_ca, user_warnings_en, user_warnings_es, user_warnings_it
from typing import Iterable, Iterator
from .common import CaptureResult
from .types.user_warnings import UserWarning
from mwtemplates import TemplateEditor

# TODO english templates are too many

# exports 
__all__ = ['user_warnings_extractor', 'UserWarning', 'lang_dict']

# https://regex101.com/r/A4fuC1/1
user_warnings_pattern = r'''
    \{\{                    # match {{
        (?:                 # non-capturing group
            \s              # match any spaces
            |               # or
            \_              # match underscore (count as space)
        )*                  # match 0 or multiple times
        (?P<type>           # namedgroup named type
            %s              # user warning word to substitute
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

# https://regex101.com/r/bVCDMJ/1
user_warnings_empty_pattern = r'''
    \{\{                    # match {{
        (?:                 # non-capturing group
            \s              # match any spaces
            |               # or
            \_              # match underscore (count as space)
        )*                  # match 0 or multiple times
        (?P<type>           # named group named type
            %s              # user warning word to substitute
        )                   # closed named group
        (?P<options>        # named group named options
            (?:             # non-capturing group
                \s          # match any spaces
                |           # or
                \_          # match _
            )*              # repeat the group 0 or n times
        )                   # end of a non captuiring group
    \}\}'''                 # match }}


# Italian user warnings words
italian_user_warnings = set(
    user_warnings_it.avviso_utenti_anonimi + \
    user_warnings_it.benvenuto + \
    user_warnings_it.benvenuto_progetti + \
    user_warnings_it.avviso_copyright + \
    user_warnings_it.avviso_invito_progetti + \
    user_warnings_it.vandalismo
)

# English user warnings words
english_user_warnings = set(
    user_warnings_en.block_templates_indefinitely_blocked_templates + \
    user_warnings_en.block_templates + \
    user_warnings_en.arbitration_enforcement_templates_1RR_related_templates + \
    user_warnings_en.arbitration_enforcement_templates_pages_with_discretionary_sanctions_editnotice + \
    user_warnings_en.arbitration_enforcement_templates + \
    user_warnings_en.csd_warning_templates + \
    user_warnings_en.community_authorised_general_sanctions_templates + \
    user_warnings_en.community_authorised_general_sanctions_templates_standardized + \
    user_warnings_en.community_authorised_general_sanctions_templates_obsolete + \
    user_warnings_en.non_english_welcome + \
    user_warnings_en.non_english + \
    user_warnings_en.test_templates + \
    user_warnings_en.standardized_templates + \
    user_warnings_en.user_warnings_templates
)

# Spanish user warnings words
spanish_user_warnings = set(
    user_warnings_es.bienvenida + \
    user_warnings_es.permission_grant_notification_templates + \
    user_warnings_es.user_warnings
)

# Catalan user warnings words
catalan_user_warnings = set(
    user_warnings_ca.benvinguda + \
    user_warnings_ca.Avisos_de_discussio + \
    user_warnings_ca.plantilles_d_avisos_d_edicio_generics + \
    user_warnings_ca.plantilles_d_avisos_d_edicio + \
    user_warnings_ca.plantilles_d_avisos_d_idioma + \
    user_warnings_ca.plantilles_d_avisos 
)

all_templates = set().union(italian_user_warnings, spanish_user_warnings, catalan_user_warnings, english_user_warnings) # for now not the english one english_user_warnings

lang_dict = {
    'it': italian_user_warnings,
    'ca': catalan_user_warnings,
    'es': spanish_user_warnings, 
    'en': english_user_warnings
}

# template category mapping dictionary
template_category_mapping = dict()
template_category_mapping.update(user_warnings_ca.plantilles_mapping)
template_category_mapping.update(user_warnings_es.plantillas_mapping)
template_category_mapping.update(user_warnings_en.template_mappings)
template_category_mapping.update(user_warnings_it.templates_mapping)

WIKIBREAKS_PATTERN_REs = [ 
    re.compile(user_warnings_pattern%(w_word.replace(' ', r'\ ')), re.IGNORECASE | re.UNICODE | re.VERBOSE | re.MULTILINE) 
    for w_word in all_templates
]

WIKIBREAKS_EMPTY_PATTERN_REs = [
    re.compile(user_warnings_empty_pattern%(w_word.replace(' ', r'\ ')), re.IGNORECASE | re.UNICODE | re.VERBOSE | re.MULTILINE) 
    for w_word in all_templates
]

WIKIBREAKS_REs = WIKIBREAKS_PATTERN_REs + WIKIBREAKS_EMPTY_PATTERN_REs

def user_warnings_extractor(text: str) -> Iterator[CaptureResult[UserWarning]]:

    # use template extractor from mwtemplates
    try:
        uwarnings = TemplateEditor(text)
    except:
        # there can be different type of text which are not supported by mwtemplates
        return user_warnings_extractor_handcrafted(text)


    # for each unique template name
    for key in uwarnings.templates.keys():

        # template name
        template_name = key.lower().strip()
        
        # associated language
        lang = None
        
        if template_name in italian_user_warnings:
            lang = 'it'
        elif template_name in catalan_user_warnings:
            lang = 'ca'
        elif template_name in spanish_user_warnings:
            lang = 'es'
        elif template_name in english_user_warnings:
            lang = 'en'

        # check if the template is needed or not
        if not lang:
            continue

        # for each template named key occurence
        for template in uwarnings.templates[key]:

            # basic parameters
            user_warnings_obj = UserWarning(template_name, lang, dict(), False, template_category_mapping[template_name])

            # Counter for positional arguments
            positional_counter = 1  # NOTE: starting from 1, as the first argument is 1 in the wikimarkup

            # for each parameter
            for i, parameters in enumerate(template.parameters):
                
                # named parameter
                if len(parameters.name.strip()) > 0:
                    user_warnings_obj.options[parameters.name] = parameters.value
                else:
                    # positional parameter
                    user_warnings_obj.options[positional_counter] = parameters.value
                    positional_counter += 1

                user_warnings_obj.at_least_one_parameter = True

            yield CaptureResult(
                data=(user_warnings_obj), span=None
            )

def user_warnings_extractor_handcrafted(text: str) -> Iterator[CaptureResult[UserWarning]]:
    for pattern in WIKIBREAKS_REs:
        for match in pattern.finditer(text): # returns an iterator of match object
            if check_wikibreaks_presence(match): # extract a named group called type (name of the user warning template used)
                # template name
                template_name = match.group('type')
                # language of that template
                lang = None
                if not template_name:
                    return
                else:
                    # language recognition
                    template_name = template_name.lower().strip()
                    if template_name in italian_user_warnings:
                        lang = 'it'
                    elif template_name in catalan_user_warnings:
                        lang = 'ca'
                    elif template_name in spanish_user_warnings:
                        lang = 'es'
                    elif template_name in english_user_warnings:
                        lang = 'en'

                # User warning object
                user_warnings_obj = UserWarning(template_name, lang, dict(), False, template_category_mapping[template_name])

                # Parse the options if any
                if check_options(match):
                    # parse the options
                    parsed_options = match.group('options').strip().replace('_', '') # retrieve the options
                    # threat differently the wikilinks in it
                    parsed_options = split_and_adjust_wikilinks(parsed_options)
                    # Counter for positional arguments
                    positional_counter = 1  # NOTE: starting from 1, as the first argument is 1 in the wikimarkup
                    # if no options are provided (note empty options means {{template}} and not {{template|}} nor {{template||}})
                    # those last two are considered as options are actually passed
                    if not (len(parsed_options) == 1 and parsed_options[0] == ''):
                        # loop over all the parsed options
                        for opt in parsed_options:
                            # Splitting for namedparameters -> note there is no way I can store all the possibile way to call a parameter, 
                            # due to lack of documentation and other things
                            name_value = opt.split('=', 1)
                            # Key and value for the option entry in the dictionary
                            key = positional_counter
                            value = name_value[0]
                            if len(name_value) > 1:
                                key, value = name_value
                            else:
                                positional_counter += 1
                            # Assign the parsed options to the user_warning_obj
                            user_warnings_obj.options[key] = value  # overritten in case of the same name of the parameters
                        # at least one parameter found
                        user_warnings_obj.at_least_one_parameter = True

                yield CaptureResult(
                    data=(user_warnings_obj), span=(match.start(), match.end())
                )

# https://stackoverflow.com/questions/42070323/split-on-spaces-not-inside-parentheses-in-python
def split_and_adjust_wikilinks(sentence: str, separator: str = "|", lparen: str = "[", rparen:str = "]") -> Iterable[str]:
    """
    Simple wikilinks detector and handler for cases where there are wikilinks in user warnings
    E.g:
    {{template|[[User:Foo|Foobar]]|motivation}}
    The options should be parsed as:
    1) [[Uesr:Foo|Foobar]] # wikilink detected!
    2) motivation
    And should also be individuated the following:
    name|[[26 agosto]],''[[Villasimius|a Villasimius]]'',[[Austria |a Vienna]] .
    """
    nb_brackets = 0
    sentence = sentence.strip(separator) # get rid of leading/trailing seps
    l = [0]
    for i,c in enumerate(sentence):
        if c == lparen:
            nb_brackets += 1
        elif c == rparen:
            nb_brackets -= 1
        elif c == separator and nb_brackets == 0:
            l.append(i)
    l.append(len(sentence))
    return([sentence[i:j].strip(separator) for i,j in zip(l,l[1:])])

def concatenate_list_values(elem_list: Iterable[str], from_index: int, to_index, concatenate_value: str) -> str:
    """Concatenates element in a list of strings starting from a starting index until the end index (included) with a custom separator"""
    result = elem_list[from_index] 
    for i in range(from_index + 1, to_index + 1):
        result += '{}{}'.format(concatenate_value, elem_list[i])
    return result

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