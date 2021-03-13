import regex as re
from ..types.language_level import LanguageLevel
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

def write_error_level_not_recognized(match: Iterator[re.Match], lev: str) -> None:
    #with open('error.txt', 'a+') as f:
    #    f.write('{} level {} not recognized\n'.format(match, lev))
    pass

def write_error(pattern: re.Pattern, match: Iterator[re.Match]) -> None:
    #with open('error.txt', 'a+') as f:
    #    f.write('pattern who failed {} match {}\n'.format(pattern, match))
    pass