from typing import Mapping

class UserWarningTf:
    """Class which stores information about the tf of the template"""

    """The pair regexp and parameters"""
    def __init__(self, template_text: str, inf_retrieval: Mapping, total_number_words: int):
        self.template_text = template_text
        self.inf_retrieval = inf_retrieval
        self.total_number_words = total_number_words

    def to_dict(self) -> Mapping:
        obj = dict()
        obj['template_text'] = self.template_text
        obj['inf_retrieval'] = self.inf_retrieval
        obj['total_number_words'] = self.total_number_words
        return obj

    def __repr__(self) -> str:
        return 'template_text: {}; inf_retrieval: {}'.format(self.template_text, self.inf_retrieval)