from typing import Mapping, Iterable

class Wikibreak:
    """Class which stores the possible attributes, if any, of a Wikipause object"""

    """The set of relevants attribute of the wikibreak"""
    def __init__(self, wikipause_name: str, user_name: str, back: str, w_type: str, message: str, additional_message: str,  not_parsed: Iterable[str]):
        self.wikipause_name = wikipause_name.strip().lower()
        self.user_name = user_name.strip()
        self.back = back.strip()
        self.w_type = w_type.strip().lower()
        self.message = message.strip()
        self.additional_message = additional_message
        self.not_parsed = not_parsed

    def to_dict(self) -> Mapping:
        """It converts the wikibreak class instance into a dictionary"""
        obj = dict()
        obj['wikipause_name'] = self.wikipause_name
        obj['user_name'] =self.user_name
        obj['back'] = self.back
        obj['type'] = self.w_type
        obj['message'] = self.message
        obj['additional_message'] = self.additional_message
        obj['not_parsed'] = self.not_parsed
        return obj

    def from_dict(self, dictionary) -> None:
        if 'wikipause_name' in dictionary:
            self.wikipause_name = dictionary['wikipause_name']
        if 'user_name' in dictionary:
            self.user_name = dictionary['user_name']
        if 'back' in dictionary:
            self.back = dictionary['back']
        if 'w_type' in dictionary:
            self.w_type = dictionary['w_type']
        if 'message' in dictionary:
            self.message = dictionary['message']
        if 'additional_message' in dictionary:
            self.additional_message = dictionary['additional_message']
        if 'not_parsed' in dictionary:
            self.not_parsed = dictionary['not_parsed']

    def __repr__(self) -> str:
        return 'wikipause_name: {}; user_name: {}, back: {}, type: {}, message: {}, additional_message: {}, notparsed: {}'.format(
            self.wikipause_name, self.user_name, self.back, self.w_type, self.message, self.additional_message, self.not_parsed)