from typing import Mapping

class UserWarningTemplate:
    """Class which stores some info about the user warnings template"""

    """The pair regexp and parameters"""
    def __init__(self, regexp: str, parameters: list, sub_templates: list):
        self.regexp = regexp
        self.parameters = parameters
        self.sub_templates = sub_templates

    def to_dict(self) -> Mapping:
        obj = dict()
        obj['regexp'] = self.regexp
        obj['parameters'] = list()
        for param in self.parameters:
            obj['parameters'].append(param)
        for template in self.sub_templates:
            obj['sub_templates'].append(template)
        return obj

    def __repr__(self) -> str:
        return 'regexp: {}; parameters: {}, sub_templates: {}'.format(self.regexp, self.parameters, self.sub_templates)