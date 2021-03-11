import re
from .language_level import LanguageLevel
from typing import Iterator

def is_level(value: str) -> bool:
    if value.lower() == 'n':
        value = LanguageLevel.MOTHER_TONGUE_LEVEL
    
    try:
        value = int(value)
        return True
    except ValueError:
        return False

def get_level(value:str) -> int:
    if value.lower() == 'n':
        value = LanguageLevel.MOTHER_TONGUE_LEVEL
    return int(value)

# pattern: re.Pattern, match: Iterator[re.Match]
def write_error_level_not_recognized(match, lev: str) -> None:
    #with open('error.txt', 'a+') as f:
    #    f.write('{} level {} not recognized\n'.format(match, lev))
    pass

# pattern: re.Pattern, match: Iterator[re.Match]
def write_error(pattern, match) -> None:
    #with open('error.txt', 'a+') as f:
    #    f.write('pattern who failed {} match {}\n'.format(pattern, match))
    pass