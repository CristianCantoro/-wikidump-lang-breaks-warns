from typing import Mapping

class UserWarningTemplate:
    """Class which stores some info about the user warnings template"""

    """The pair regexp and parameters"""
    def __init__(self, regexp: str, parameters: list):
        self.regexp = regexp
        self.parameters = parameters

    def to_dict(self) -> Mapping:
        obj = dict()
        obj['regexp'] = self.regexp
        obj['parameters'] = list()
        for param in self.parameters:
            obj['parameters'].append(param)
        return obj

    def __repr__(self) -> str:
        return 'regexp: {}; parameters: {}'.format(self.regexp, self.parameters)