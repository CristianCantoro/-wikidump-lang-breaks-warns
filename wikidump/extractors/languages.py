"""Extractor for "languages" known by Wikipedians in their personal page https://en.wikipedia.org/wiki/Wikipedia:Babel. 

Common example of Wikipedia:Babel template
{{Babel|zh|es-4|ru-2}}

Please not there is also this extension of Babel that should be considered: https://www.mediawiki.org/wiki/Extension:Babel#Usage
{{Babel-5|ca|es-3|en-2|fr-2|de-1}}

There are also some alternatives to the Babel template:
    - standalone language templates. Format: {{User xx-1}}{{User yy-1}}{{User zz-1}}. https://en.wikipedia.org/wiki/Category:Language_user_templates
    - Babel-N template. Format: {{Babel-N|1={{User xx-1}}{{User yy-1}}{{User zz-1}}}} https://en.wikipedia.org/wiki/Template:Babel-N
    - top and bottom templates to make the box. Format: {{Userboxtop}}{{User xx-1}}{{User yy-1}}{{User zz-1}}{{Userboxbottom}}. https://en.wikipedia.org/wiki/Template:Userboxtop https://en.wikipedia.org/wiki/Template:Userboxbottom
    - Babel extension. Format: {{#Babel:xx|yy-1|zz-2}}  # https://www.mediawiki.org/wiki/Extension:Babel#Usage
"""
import regex as re
from typing import Iterator

from .common import CaptureResult, Identifier, Span

def language_knowledge(source: str) -> None: # todo modify the returned type should not be NONE
    pass