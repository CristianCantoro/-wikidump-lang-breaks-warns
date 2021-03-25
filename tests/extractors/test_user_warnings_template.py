import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', 'wikidump'))
import collections
from wikidump.extractors import user_warnings_template

INPUT_TEXT = """
<includeonly>This is a sample template</includeonly>
<includeonly><noinclude>This is a sample template</noinclude> part 2</includeonly>
<includeonly>Hi there</includeonly>
"""

def wikibreaks_extractor():
    new_regex = user_warnings_template.userwarnings_regex_extractor(INPUT_TEXT)
    print('{}'.format(new_regex))

if __name__ == "__main__":
    wikibreaks_extractor()