import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', 'wikidump'))
import collections
from wikidump.extractors import user_warnings_template

INPUT_TEXT = """
<onlyinclude>This is a sample template</onlyinclude>
<onlyinclude><onlyinclude>This is a sample template</onlyinclude> part 2</onlyinclude>
<onlyinclude>Hi there</onlyinclude>
"""

def wikibreaks_extractor():
    new_regex = user_warnings_template.userwarnings_regex_extractor(INPUT_TEXT)
    print('{}'.format(new_regex))

if __name__ == "__main__":
    wikibreaks_extractor()