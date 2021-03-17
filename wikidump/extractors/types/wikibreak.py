from typing import Mapping, Iterable

class Wikibreak:
    """Class which stores the possible attributes, if any, of a wikibreak object"""

    """The set of relevants attribute of the wikibreak"""
    def __init__(self, wikibreak_name: str, wikibreak_category: Iterable[str], wikibreak_subcategory: str,options: Mapping, at_least_one_parameter: bool):
        if all(isinstance(i, list) for i in wikibreak_category):
            wikibreak_category = wikibreak_category[0]
        self.wikibreak_category = wikibreak_category                    # main category: eg: break, mental, other, ecc
        self.wikibreak_subcategory = wikibreak_subcategory              # sub category: bonked, wikibreak, computer death ecc..
        self.wikibreak_name = wikibreak_name.strip().lower()            # name of the wikibreak used, for example viqudescansas, wikipausa ecc..
        self.options = options                                          # wikibreak options
        self.at_least_one_parameter = at_least_one_parameter            # boolean value which tells if the wikibreak contains at least an option

    def to_dict(self) -> Mapping:
        """It converts the wikibreak class instance into a dictionary"""
        obj = dict()
        obj['wikibreak_name'] = self.wikibreak_name
        obj['wikibreak_category'] = list()
        for el in self.wikibreak_category:
            obj['wikibreak_category'].append(el)
        obj['wikibreak_subcategory'] = self.wikibreak_subcategory
        obj['at_least_one_parameter'] = self.at_least_one_parameter
        obj['options'] = self.options
        return obj

    def __repr__(self) -> str:
        return 'wikibreak_name: {}; options: {}; category: {}; subcategory: {}; at_least_one_parameter: {}'.format(
            self.wikibreak_name, self.options, self.wikibreak_category, self.wikibreak_subcategory, self.at_least_one_parameter)