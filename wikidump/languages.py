import json

supported = {'de', 'en', 'es', 'fr', 'it', 'nl', 'pl', 'ru', 'sv'}

bibliography = {
    'en': {
        'bibliography',
        'references',
        'reference',
        'further reading',
        'notes',
        'sources',
        'footnotes',
        'citations',
        'publications',
        'publication history',
        'literature',
    },
    'it': {'bibliografia'},
}

citation = {
    'en': {'Citation', 'cite', 'vcite'},
}

iso639_languages = {'ab': 'Abkhazian', 'abk': 'Abkhazian', 'aa': 'Afar', 'aar': 'Afar', 'af': 'Afrikaans', 'afr': 'Afrikaans', 'ak': 'Akan', 'aka': 'Akan', 'aka + ': 'Akan', 'sq': 'Albanian', 'sqi': 'Albanian', 'alb': 'Albanian', 'sqi + ': 'Albanian', 'am': 'Amharic', 'amh': 'Amharic', 'ar': 'Arabic', 'ara': 'Arabic', 'ara + ': 'Arabic', 'an': 'Aragonese', 'arg': 'Aragonese', 'hy': 'Armenian', 'hye': 'Armenian', 'arm': 'Armenian', 'as': 'Assamese', 'asm': 'Assamese', 'av': 'Avaric', 'ava': 'Avaric', 'ae': 'Avestan', 'ave': 'Avestan', 'ay': 'Aymara', 'aym': 'Aymara', 'aym + ': 'Aymara', 'az': 'Azerbaijani', 'aze': 'Azerbaijani', 'aze + ': 'Azerbaijani', 'bm': 'Bambara', 'bam': 'Bambara', 'ba': 'Bashkir', 'bak': 'Bashkir', 'eu': 'Basque', 'eus': 'Basque', 'baq': 'Basque', 'be': 'Belarusian', 'bel': 'Belarusian', 'bn': 'Bengali', 'ben': 'Bengali', 'bh': 'Bihari languages', 'bih': 'Bihari languages', 'bi': 'Bislama', 'bis': 'Bislama', 'bs': 'Bosnian', 'bos': 'Bosnian', 'br': 'Breton', 'bre': 'Breton', 'bg': 'Bulgarian', 'bul': 'Bulgarian', 'my': 'Burmese', 'mya': 'Burmese', 'bur': 'Burmese', 'ca': 'Catalan', 'cat': 'Catalan', 'ch': 'Chamorro', 'cha': 'Chamorro', 'ce': 'Chechen', 'che': 'Chechen', 'ny': 'Chichewa', 'nya': 'Chichewa', 'zh': 'Chinese', 'zho': 'Chinese', 'chi': 'Chinese', 'zho + ': 'Chinese', 'cv': 'Chuvash', 'chv': 'Chuvash', 'kw': 'Cornish', 'cor': 'Cornish', 'co': 'Corsican', 'cos': 'Corsican', 'cr': 'Cree', 'cre': 'Cree', 'cre + ': 'Cree', 'hr': 'Croatian', 'hrv': 'Croatian', 'cs': 'Czech', 'ces': 'Czech', 'cze': 'Czech', 'da': 'Danish', 'dan': 'Danish', 'dv': 'Divehi', 'div': 'Divehi', 'nl': 'Dutch', 'nld': 'Dutch', 'dut': 'Dutch', 'dz': 'Dzongkha', 'dzo': 'Dzongkha', 'en': 'English', 'eng': 'English', 'eo': 'Esperanto', 'epo': 'Esperanto', 'et': 'Estonian', 'est': 'Estonian', 'est + ': 'Estonian', 'ee': 'Ewe', 'ewe': 'Ewe', 'fo': 'Faroese', 'fao': 'Faroese', 'fj': 'Fijian', 'fij': 'Fijian', 'fi': 'Finnish', 'fin': 'Finnish', 'fr': 'French', 'fra': 'French', 'fre': 'French', 'ff': 'Fulah', 'ful': 'Fulah', 'ful + ': 'Fulah', 'gl': 'Galician', 'glg': 'Galician', 'ka': 'Georgian', 'kat': 'Georgian', 'geo': 'Georgian', 'de': 'German', 'deu': 'German', 'ger': 'German', 'el': 'Greek', 'ell': 'Greek', 'gre': 'Greek', 'gn': 'Guarani', 'grn': 'Guarani', 'grn + ': 'Guarani', 'gu': 'Gujarati', 'guj': 'Gujarati', 'ht': 'Haitian', 'hat': 'Haitian', 'ha': 'Hausa', 'hau': 'Hausa', 'he': 'Hebrew', 'heb': 'Hebrew', 'hz': 'Herero', 'her': 'Herero', 'hi': 'Hindi', 'hin': 'Hindi', 'ho': 'Hiri Motu', 'hmo': 'Hiri Motu', 'hu': 'Hungarian', 'hun': 'Hungarian', 'ia': 'Interlingua', 'ina': 'Interlingua', 'id': 'Indonesian', 'ind': 'Indonesian', 'ie': 'Interlingue', 'ile': 'Interlingue', 'ga': 'Irish', 'gle': 'Irish', 'ig': 'Igbo', 'ibo': 'Igbo', 'ik': 'Inupiaq', 'ipk': 'Inupiaq', 'ipk + ': 'Inupiaq', 'io': 'Ido', 'ido': 'Ido', 'is': 'Icelandic', 'isl': 'Icelandic', 'ice': 'Icelandic', 'it': 'Italian', 'ita': 'Italian', 'iu': 'Inuktitut', 'iku': 'Inuktitut', 'iku + ': 'Inuktitut', 'ja': 'Japanese', 'jpn': 'Japanese', 'jv': 'Javanese', 'jav': 'Javanese', 'kl': 'Kalaallisut', 'kal': 'Kalaallisut', 'kn': 'Kannada', 'kan': 'Kannada', 'kr': 'Kanuri', 'kau': 'Kanuri', 'kau + ': 'Kanuri', 'ks': 'Kashmiri', 'kas': 'Kashmiri', 'kk': 'Kazakh', 'kaz': 'Kazakh', 'km': 'Central Khmer', 'khm': 'Central Khmer', 'ki': 'Kikuyu', 'kik': 'Kikuyu', 'rw': 'Kinyarwanda', 'kin': 'Kinyarwanda', 'ky': 'Kirghiz', 'kir': 'Kirghiz', 'kv': 'Komi', 'kom': 'Komi', 'kom + ': 'Komi', 'kg': 'Kongo', 'kon': 'Kongo', 'kon + ': 'Kongo', 'ko': 'Korean', 'kor': 'Korean', 'ku': 'Kurdish', 'kur': 'Kurdish', 'kur + ': 'Kurdish', 'kj': 'Kuanyama', 'kua': 'Kuanyama', 'la': 'Latin', 'lat': 'Latin', 'lb': 'Luxembourgish', 'ltz': 'Luxembourgish', 'lg': 'Ganda', 'lug': 'Ganda', 'li': 'Limburgan', 'lim': 'Limburgan', 'ln': 'Lingala', 'lin': 'Lingala', 'lo': 'Lao', 'lao': 'Lao', 'lt': 'Lithuanian', 'lit': 'Lithuanian', 'lu': 'Luba-Katanga', 'lub': 'Luba-Katanga', 'lv': 'Latvian', 'lav': 'Latvian', 'lav + ': 'Latvian', 'gv': 'Manx', 'glv': 'Manx', 'mk': 'Macedonian', 'mkd': 'Macedonian', 'mac': 'Macedonian', 'mg': 'Malagasy', 'mlg': 'Malagasy', 'mlg + ': 'Malagasy', 'ms': 'Malay', 'msa': 'Malay', 'may': 'Malay', 'msa + ': 'Malay', 'ml': 'Malayalam', 'mal': 'Malayalam', 'mt': 'Maltese', 'mlt': 'Maltese', 'mi': 'Maori', 'mri': 'Maori', 'mao': 'Maori', 'mr': 'Marathi', 'mar': 'Marathi', 'mh': 'Marshallese', 'mah': 'Marshallese', 'mn': 'Mongolian', 'mon': 'Mongolian', 'mon + ': 'Mongolian', 'na': 'Nauru', 'nau': 'Nauru', 'nv': 'Navajo', 'nav': 'Navajo', 'nd': 'North Ndebele', 'nde': 'North Ndebele', 'ne': 'Nepali', 'nep': 'Nepali', 'nep + ': 'Nepali', 'ng': 'Ndonga', 'ndo': 'Ndonga', 'nb': 'Norwegian Bokm\u00e5l', 'nob': 'Norwegian Bokm\u00e5l', 'nn': 'Norwegian Nynorsk', 'nno': 'Norwegian Nynorsk', 'no': 'Norwegian', 'nor': 'Norwegian', 'nor + ': 'Norwegian', 'ii': 'Sichuan Yi', 'iii': 'Sichuan Yi', 'nr': 'South Ndebele', 'nbl': 'South Ndebele', 'oc': 'Occitan', 'oci': 'Occitan', 'oj': 'Ojibwa', 'oji': 'Ojibwa', 'oji + ': 'Ojibwa', 'cu': 'Church\u00a0Slavic', 'chu': 'Church\u00a0Slavic', 'om': 'Oromo', 'orm': 'Oromo', 'orm + ': 'Oromo', 'or': 'Oriya', 'ori': 'Oriya', 'ori + ': 'Oriya', 'os': 'Ossetian', 'oss': 'Ossetian', 'pa': 'Punjabi', 'pan': 'Punjabi', 'pi': 'Pali', 'pli': 'Pali', 'fa': 'Persian', 'fas': 'Persian', 'per': 'Persian', 'fas + ': 'Persian', 'pl': 'Polish', 'pol': 'Polish', 'ps': 'Pashto', 'pus': 'Pashto', 'pus + ': 'Pashto', 'pt': 'Portuguese', 'por': 'Portuguese', 'qu': 'Quechua', 'que': 'Quechua', 'que + ': 'Quechua', 'rm': 'Romansh', 'roh': 'Romansh', 'rn': 'Rundi', 'run': 'Rundi', 'ro': 'Romanian', 'ron': 'Romanian', 'rum': 'Romanian', 'ru': 'Russian', 'rus': 'Russian', 'sa': 'Sanskrit', 'san': 'Sanskrit', 'sc': 'Sardinian', 'srd': 'Sardinian', 'srd + ': 'Sardinian', 'sd': 'Sindhi', 'snd': 'Sindhi', 'se': 'Northern Sami', 'sme': 'Northern Sami', 'sm': 'Samoan', 'smo': 'Samoan', 'sg': 'Sango', 'sag': 'Sango', 'sr': 'Serbian', 'srp': 'Serbian', 'gd': 'Gaelic', 'gla': 'Gaelic', 'sn': 'Shona', 'sna': 'Shona', 'si': 'Sinhala', 'sin': 'Sinhala', 'sk': 'Slovak', 'slk': 'Slovak', 'slo': 'Slovak', 'sl': 'Slovenian', 'slv': 'Slovenian', 'so': 'Somali', 'som': 'Somali', 'st': 'Southern Sotho', 'sot': 'Southern Sotho', 'es': 'Spanish', 'spa': 'Spanish', 'su': 'Sundanese', 'sun': 'Sundanese', 'sw': 'Swahili', 'swa': 'Swahili', 'swa + ': 'Swahili', 'ss': 'Swati', 'ssw': 'Swati', 'sv': 'Swedish', 'swe': 'Swedish', 'ta': 'Tamil', 'tam': 'Tamil', 'te': 'Telugu', 'tel': 'Telugu', 'tg': 'Tajik', 'tgk': 'Tajik', 'th': 'Thai', 'tha': 'Thai', 'ti': 'Tigrinya', 'tir': 'Tigrinya', 'bo': 'Tibetan', 'bod': 'Tibetan', 'tib': 'Tibetan', 'tk': 'Turkmen', 'tuk': 'Turkmen', 'tl': 'Tagalog', 'tgl': 'Tagalog', 'tn': 'Tswana', 'tsn': 'Tswana', 'to': 'Tonga', 'ton': 'Tonga', 'tr': 'Turkish', 'tur': 'Turkish', 'ts': 'Tsonga', 'tso': 'Tsonga', 'tt': 'Tatar', 'tat': 'Tatar', 'tw': 'Twi', 'twi': 'Twi', 'ty': 'Tahitian', 'tah': 'Tahitian', 'ug': 'Uighur', 'uig': 'Uighur', 'uk': 'Ukrainian', 'ukr': 'Ukrainian', 'ur': 'Urdu', 'urd': 'Urdu', 'uz': 'Uzbek', 'uzb': 'Uzbek', 'uzb + ': 'Uzbek', 've': 'Venda', 'ven': 'Venda', 'vi': 'Vietnamese', 'vie': 'Vietnamese', 'vo': 'Volap\u00fck', 'vol': 'Volap\u00fck', 'wa': 'Walloon', 'wln': 'Walloon', 'cy': 'Welsh', 'cym': 'Welsh', 'wel': 'Welsh', 'wo': 'Wolof', 'wol': 'Wolof', 'fy': 'Western Frisian', 'fry': 'Western Frisian', 'xh': 'Xhosa', 'xho': 'Xhosa', 'yi': 'Yiddish', 'yid': 'Yiddish', 'yid + ': 'Yiddish', 'yo': 'Yoruba', 'yor': 'Yoruba', 'za': 'Zhuang', 'zha': 'Zhuang', 'zha + ': 'Zhuang', 'zu': 'Zulu', 'zul': 'Zulu'}

"""
What I mean for:
* References: a section containing footnotes for works cited in the text.
* Bibliography: a section containing articles and journals.
* Further reading: like `Bibliography`, but contains references not used in the text.
* Footnotes: a section containing explainations to concepts.

From now on, words in backquotes (`) are to be interpreted as concept using the above definitions, while words in double quotes (") are to be interpreted as terms found in the text of the articles.

"References" (term) is commonly used as `Bibliography` (concept), i.e. articles and journals without backref to the text.
And, of course, "Bibliography" (term) is sometimes used as `References` (concept).
* https://en.wikipedia.org/w/index.php?title=Anabaptists&oldid=49953891 "References" interpreted as `Bibliography`
* https://en.wikipedia.org/w/index.php?title=Alcopop&oldid=296736852 "References" interpreted as `Bibliography`
* https://en.wikipedia.org/w/index.php?title=Amu%20Darya&oldid=66374611 "References" interpreted as `Bibliography`

"Citations" (term) sometimes used as synonym for "References" or "Bibliography" (terms):
* https://en.wikipedia.org/w/index.php?title=Augustine_of_Canterbury&oldid=676642624 "Citations" used as `References`, "References" used as `Bibliography`
* https://en.wikipedia.org/w/index.php?title=Anemometer&oldid=674186492#Citations "Citations" used as `References`

"Notes and References" and "References and Notes" (terms) are used as synonyms for "References" (term):
* https://en.wikipedia.org/w/index.php?title=Ackermann%20function&oldid=335603599#Notes_and_references "Notes and References" converted to "References" (term) and interpreted as `References`
* https://en.wikipedia.org/w/index.php?title=albanians&oldid=391045161#Notes_and_references "Notes and References" is a wrapper around "Notes" (interpreted as `footnotes`) and "References" (interpreted as `References`)
* https://en.wikipedia.org/w/index.php?title=assassination&oldid=678057527#Notes_and_references interpreted as `References`

"Sources" seems to be interpreted as `Bibliography` or `References`, and sometimes then converted by users to "References" or "Bibliography"
* https://en.wikipedia.org/w/index.php?title=artemis&diff=next&oldid=565871969 "Sources" has been converted to "References and sources"
* https://en.wikipedia.org/w/index.php?title=Amakusa&direction=next&oldid=667294099 "Sources" used as `Bibliography`
* https://en.wikipedia.org/w/index.php?title=A%20Doll's%20House&oldid=676505492#Sources "Sources" used as `Bibliography`
* https://en.wikipedia.org/w/index.php?title=A.%20E.%20Housman&diff=next&oldid=678259900#Sources "Sources" used `Bibliography`

"Footnotes" is commonly interpreted as `References`, with the following terms: "References" and "Citations"
* https://en.wikipedia.org/w/index.php?title=Augustine%20of%20Canterbury&oldid=459457206#Footnotes "Footnotes" is used as `References`; "Footnotes" is then converted to "Citations", used as `References`
* https://en.wikipedia.org/w/index.php?title=Amoxicillin&diff=next&oldid=423375138 "Footnotes" used as and converted to `References`
* https://en.wikipedia.org/w/index.php?title=Anabaptists&oldid=49953891#Footnotes_and_references "Footnotes" interpreted as `References`. The next revision converts "Footnotes" to "Footnotes and References".
* https://en.wikipedia.org/w/index.php?title=Alcopop&oldid=296736852#Footnotes "Footnotes" used as `References`
* https://en.wikipedia.org/w/index.php?title=Archaeopteryx&diff=next&oldid=326796096 "Footnotes" interpreteda s and then converted to `References` (term and concept)
* https://en.wikipedia.org/w/index.php?title=Al%20Capp&oldid=590148186#Footnotes "Footnotes" interpreted as `References`. It is then converted to "Notes"
* https://en.wikipedia.org/w/index.php?title=Amu%20Darya&oldid=66374611#Footnotes "Footnotes" interpreted as `References`. Later converted to "Notes"
* https://en.wikipedia.org/w/index.php?title=Albert%20Brooks&oldid=150996845#Footnotes "Footnotes" used as and then converted to `References` (term and concept)

"Literature" is used most of the times as a subsection for things like "Culture", and in some cases is a replacement for "bibliography":
* https://en.wikipedia.org/w/index.php?title=Alexandria&oldid=678355005 "Literature" used as subsection of "Culture"
* https://en.wikipedia.org/w/index.php?title=Bible&oldid=23508742#Literature "Literature" used as `Bibliography`
* https://en.wikipedia.org/w/index.php?title=Board_game&oldid=7131437#Literature "Literature" used as "Bibliography", then converted to "References" (used as "Bibliography")
* https://en.wikipedia.org/w/index.php?title=Ahuitzotl&oldid=118183827 "Literature" interpreted as `Bibliography`

"Publications" and "Publication history" are used as a subsection for the "Biography" with the works of the person described.

"Reference" is almost always converted to "References" in a successive revision.


"Notes" is sometimes interpreted as `References` or `Footnotes`
* https://en.wikipedia.org/w/index.php?title=Ahuitzotl&oldid=118183827 "Notes" used as `Footnotes`
* https://en.wikipedia.org/w/index.php?title=Archaeoastronomy&oldid=678777218#Notes "Notes" used as `References`
* https://en.wikipedia.org/w/index.php?title=Alexander_of_Hales&oldid=661215939#Other_historical_works "Notes" interpreted as `References`

"See also" and "Related pages" usually contain links to other wikipedia pages.
"""
