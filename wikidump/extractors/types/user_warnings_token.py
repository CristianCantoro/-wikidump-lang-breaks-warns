from typing import Mapping

class UserWarningTokens:
    """Class which stores some info about the user warnings tokens found in a user talk page according to a template mapping"""

    """The pair regexp and parameters"""
    def __init__(self, name: str, template_tokens: list):
        self.name = name
        self.template_tokens = template_tokens

    def to_dict(self) -> Mapping:
        obj = dict()
        obj['name'] = self.name
        obj['template_tokens'] = list()
        for token in self.template_tokens:
            obj['parameters'].append(token)
        return obj

    def __repr__(self) -> str:
        return 'name: {}; template_tokens: {}'.format(self.name, self.template_tokens)