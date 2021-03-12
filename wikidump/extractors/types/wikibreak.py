from typing import Mapping

class Wikibreak:
    """Class which stores the possible attributes, if any, of a Wikipause object"""

    """The set of relevants attribute of the wikibreak"""
    def __init__(self, wikipause_name: str, user_name: str, back: str, w_type: str, message: str):
        self.wikipause_name = wikipause_name.strip().lower()
        self.user_name = user_name.strip()
        self.back = back.strip()
        self.w_type = w_type.strip().lower() # TODO be carefull here, should be the same, probably yes, it should be checked if possible
        self.message = message.strip()

    def to_dict(self) -> Mapping:
        """It converts the wikibreak class instance into a dictionary"""
        obj = dict()
        obj['wikipause_name'] = self.wikipause_name
        obj['user_name'] =self.user_name
        obj['back'] = self.back
        obj['type'] = self.w_type
        obj['message'] = self.message
        return obj

    def __repr__(self) -> str:
        return 'wikipause_name: {}; user_name: {}, back: {}, type: {}, message: {}'.format(
            self.wikipause_name, self.user_name, self.back, self.w_type, self.message)