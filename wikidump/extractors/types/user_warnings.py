from typing import Mapping

class UserWarning:
    """Class which stores the possible attributes, if any, of a user warning object"""

    """The set of relevants attribute of the user warning"""
    def __init__(self, user_warning_name: str, lang: str, options: Mapping, at_least_one_parameter: bool, category: str):
        self.user_warning_name = user_warning_name.strip().lower()      # name of the user warning template
        self.options = options                                          # user warning options
        self.at_least_one_parameter = at_least_one_parameter            # boolean value which tells if the user warning contains at least an option
        self.lang = lang                                                # language
        self.category = category                                        # category

    def to_dict(self) -> Mapping:
        """It converts the user warning class instance into a dictionary"""
        obj = dict()
        obj['user_warning_name'] = self.user_warning_name
        obj['lang'] = self.lang
        obj['at_least_one_parameter'] = self.at_least_one_parameter
        obj['options'] = self.options
        obj['category'] = self.category
        return obj

    def __repr__(self) -> str:
        return 'user warning name: {}; options: {}; at_least_one_parameter: {}'.format(
            self.user_warning_name, self.options, self.at_least_one_parameter)