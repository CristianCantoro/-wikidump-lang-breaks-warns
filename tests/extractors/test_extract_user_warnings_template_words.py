import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', 'wikidump'))
import collections
from wikidump.extractors import user_warnings_template_words

# https://en.wikipedia.org/w/index.php?title=Template:Infobox_basketball_biography&action=edit&oldid=65638045

INPUT_TEXT = """
<table class="infobox" style="float: right; margin-left: 1em; width: 22em; font-size: 90%; clear: right;" cellspacing="3"><caption colspan="2" style="text-align: center; font-size: larger; font-weight: bold;">{{{name|{{PAGENAME}}}}}</caption>{{#if:{{{image|}}}|
<tr><td colspan="2" padding: 1em 0em;"> [[Image:{{{image}}}|{{#if:{{{image_size|}}}|{{{image_size}}}|200x250}}px|center|{{{caption|&#32;}}}]]</td></tr>
}}<tr><th style="text-align: right;">Position</th><td>{{{position}}}</td></tr>
{{#if:{{{nickname|}}}|<tr><th style="text-align: right;">Nickname</th><td>{{{nickname}}}<tr><th {{{league|}}}|<tr><th style="text-align: right;">League</th><td>{{{league}}}</td></tr>
}}<tr><th style="text-align: right;">Height</th><td>{{#if:{{{height_ft|}}}{{{height_in|}}}
| {{height|ft = {{{height_ft|0}}}|in = {{{height_in|0}}} | }}
| {{{height}}}
}}</td></tr>
<tr><th style="text-align: right;">Weight</th><td>{{#if:{{{weight_lbs|{{{weight_lb|}}}}}}
| {{weight|lbs = {{{weight_lbs|{{{weight_lb|0}}}}}} | }}
| {{{weight}}}
}}</td></tr>{{#if:{{{team|}}}
|<tr><th style="text-align: right;">Team</th><td>{{{team}}}</td></tr>
}}{{#if:{{{nationality|}}}
| <tr><th style="text-align: right;">Nationality</th>
<td>{{flagcountry|{{{nationality|}}}|}}{{#if:{{{nationality_2|}}}
  | &#32;/<br/>{{flagcountry|{{{nationality_2}}}|}}
  }}</td></tr>
}}<tr><th style="text-align: right;">Born</th><td>{{{birth_date}}}{{#if:{{{birth_place|}}}
| <br/>{{{birth_place}}}
}}</td></tr>{{#if:{{{death_date|}}}
| <tr><th style="text-align: right;">Died</th><td>{{{death_date}}}{{#if:{{{death_place|}}}
  | <br/>{{{death_place}}}
  }}</td></tr>
}}{{#if:{{{highschool|}}}
| <tr><th style="text-align: right;">High school</th><td>{{{highschool}}}</td></tr>
}}{{#if:{{{college|}}}
| <tr><th style="text-align: right;">College</th><td>{{{college}}}</td></tr>
}}{{#if:{{{pro_club|}}}
| <tr><th style="text-align: right;">Pre-draft club</th><td>{{{pro_club}}}</td></tr>
}}{{#if:{{{draft|}}}
| <tr><th style="text-align: right;">Draft</th><td>{{{draft}}}{{#if:{{{draft_year|}}}
  |, [[{{{draft_year}}} NBA Draft|{{{draft_year}}}]] {{#if:{{{draft_team|}}}
    | <br/>{{{draft_team}}}
    }}
  }}</td></tr>
}}<tr><th style="text-align: right;">Pro career</th><td>{{{career_start|{{{draft_year|&#123;&#123;&#123;career_start&#125;&#125;&#125;}}} }}} &ndash; {{#if:{{{career_end|}}}
  | {{{career_end}}}
  | ''present''
}}</td></tr>{{#if:{{{former_teams|}}}
| <tr style="vertical-align: top; padding: 1em;"><th style="text-align: right;">Former teams</th>
<td>{{{former_teams}}}</td></tr>
}}{{#if:{{{awards|}}}
| <tr style="vertical-align: top; padding: 1em;"><th style="text-align: right;">Awards</th><td>{{{awards}}}</td></tr>
}}{{#if:{{{halloffame|}}}
| <tr style="vertical-align: top; padding: 1em;"><th style="text-align: right;">Hall of Fame</th><td>{{{halloffame}}}</td></tr>
}}</table><noinclude>
:''See [[{{TALKPAGENAME}}|talk page]] for example usage.''
[[Category:Templates using ParserFunctions|Infobox NBA Player]]
[[Category:people infobox templates|NBA Player]]
[[Category:sports infobox templates|NBA Player]]
</noinclude>
"""

def user_warnings_extractor():
    obj = user_warnings_template_words.userwarnings_words_extractor(INPUT_TEXT, 'english', False)
    print('{}'.format(obj))

if __name__ == "__main__":
    user_warnings_extractor()