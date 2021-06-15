from ..types.language_level import LanguageLevel

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