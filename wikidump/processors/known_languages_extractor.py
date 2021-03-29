"""Extract the language known by the registered users in Wikipedia and some statistics about them"""

import collections
import json
import more_itertools
import mwxml
import datetime
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional
from backports.datetime_fromisoformat import MonkeyPatch

from .. import dumper, extractors, languages, utils

# Polyfiller for retrocompatibiliy with Python3.5
MonkeyPatch.patch_fromisoformat()

# REVISION AND PAGE CLASSES

class Revision:
    """Class which represent a revision of the user page"""
    def __init__(self, id: str, user: mwxml.Revision.User, timestamp: str, languages: Iterable[extractors.languages.LanguageLevel], num_langs_known: int):
        self.id = id                            # revision id
        self.user = user                        # revision user
        self.timestamp = timestamp              # revision timestamp
        self.languages = languages              # set of the languages associated with the user in that revision of his or her user page
        self.num_langs_known = num_langs_known  # number of language known by the user

    def to_dict(self) -> str:
        """Converts the object instance into a dictionary"""
        obj = dict()
        obj['id'] = self.id
        obj['user_id'] = self.user.id
        obj['user_name'] = self.user.text
        obj['timestamp'] = self.timestamp
        obj['num_languages_declared'] = self.num_langs_known
        obj['languages'] = list()
        for lang in self.languages:
            obj['languages'].append(lang.to_dict())
        return obj

class Page:
    """Class which represent a page containing a list of revisions"""
    def __init__(self, id: str, namespace: str, title: str, revisions: Iterator[Revision], num_langs_known: int):
        self.id = id                            # page id
        self.namespace = namespace              # page namespace
        self.title = title                      # page title
        self.revisions = revisions              # list of revisions
        self.num_langs_known = num_langs_known  # number of languages known

    def to_dict(self) -> Mapping:
        """Converts the object instance into a dictionary"""
        obj = dict()
        obj['id'] = self.id
        obj['namespace'] = self.namespace
        obj['title'] = self.title
        obj['revisions'] = list()
        for rev in self.revisions:
            obj['revisions'].append(rev.to_dict())
        return obj

def count_languages_occurences(language_knowledge_levels_list: Iterable[extractors.languages.LanguageLevel]) -> int:
    """Count the unique names of the languages stored in language_knowledge_levels_list list"""
    langs_set = set()
    counter = 0
    for lang_knowledge in language_knowledge_levels_list:
        if not lang_knowledge.lang in langs_set:
            counter += 1
            langs_set.add(lang_knowledge.lang)
    return counter

def extract_revisions(
        mw_page: mwxml.Page,
        stats: Mapping,
        only_last_revision: bool,
        only_revisions_with_languages: bool) -> Iterator[Revision]:
    
    """Extracts the known languages within a user page."""
    revisions = more_itertools.peekable(mw_page)

    # Newest revisions, useful only if the only_last_revision flag is set equal to true
    newest_revision = None

    for mw_revision in revisions:
        utils.dot()

        # check if it's last revision
        is_last_revision = not utils.has_next(revisions)

        # remove html comments
        text = utils.remove_comments(mw_revision.text or '')

        # It extracts a list of LanguageLevel instances, composed of (languages and it's level)
        languages = [lang for lang, _ in extractors.languages.language_knowledge(text)]

        # number of languages that the user said they know
        num_langs_known = count_languages_occurences(languages)

        # Update stats
        if not only_last_revision or (only_last_revision and is_last_revision):
            for l in languages:
                if l.lang in stats['users']['languages']:
                    # not to exceed the indices of the list
                    if 0 <= l.level < len(stats['users']['languages'][l.lang]['knowledge']):
                        stats['users']['languages'][l.lang]['knowledge'][l.level] += 1
                else:
                    stats['users']['languages'][l.lang] = dict()
                    stats['users']['languages'][l.lang]['knowledge'] = [0] * (extractors.languages.LanguageLevel.MOTHER_TONGUE_LEVEL + 1)
                    stats['users']['languages'][l.lang]['knowledge'][l.level] = 1

        # Build the revision
        rev = Revision(
            id=mw_revision.id,
            user=mw_revision.user,
            timestamp=mw_revision.timestamp.to_json(),
            languages=languages,
            num_langs_known=num_langs_known
        )

        # Check the oldest revisions possible
        if not newest_revision:
            newest_revision = rev
        else:
            newest_date = datetime.datetime.fromisoformat(newest_revision.timestamp.replace('Z', '+00:00'))
            current_date = datetime.datetime.fromisoformat(mw_revision.timestamp.to_json().replace('Z', '+00:00'))
            # change the revision if the current one is newer
            if newest_date < current_date:
                newest_revision = rev

        # Return only the revisions with at least one language if the flag's active
        stats['performance']['revisions_analyzed'] += 1
        
        # Yield when requested

        # requested only the last revision
        if only_last_revision:
            # asked for revisions with languages
            if only_revisions_with_languages:
                # has the languages list not empty
                if newest_revision.languages and is_last_revision:
                    yield newest_revision
            elif is_last_revision:
                yield newest_revision
        elif only_revisions_with_languages:
            if languages:
                yield rev
        else:
            yield rev

def extract_pages(
        dump: Iterable[mwxml.Page],
        stats: Mapping,
        only_last_revision: bool,
        only_pages_with_languages: bool,
        only_revisions_with_languages: bool) -> Iterator[Page]:
    """Extract known languages from an user page."""

    # Loop on all the pages in the dump, one at a time
    for mw_page in dump:
        utils.log("Processing", mw_page.title)
        
        # Skip non-user pages, according to https://en.wikipedia.org/wiki/Wikipedia:Namespace
        if mw_page.namespace != 2:
            utils.log('Skipped (namespace != 2)')
            continue
        
        revisions_generator = extract_revisions(
            mw_page,
            stats=stats,
            only_last_revision=only_last_revision,
            only_revisions_with_languages=only_revisions_with_languages
        )

        revisions_list = list(revisions_generator)

        page = Page(
            id=mw_page.id,
            namespace=mw_page.namespace,
            title=mw_page.title,
            revisions=revisions_list,
            num_langs_known=sum(rev.num_langs_known for rev in revisions_list)
        )

        # Return only the pages with at least one language if the flag's active
        if only_pages_with_languages:
            if page.num_langs_known > 0:
                stats['users']['total'] += 1
                yield page
        else:
            stats['users']['total'] += 1
            yield page

        stats['performance']['pages_analyzed'] += 1

def configure_subparsers(subparsers):
    """Configure a new subparser for the known languages."""
    parser = subparsers.add_parser(
        'extract-known-languages',
        help='Extract the languages known by the users',
    )
    parser.add_argument(
        '--only-pages-with-languages',
        action='store_true',
        help='Consider only the pages with at least a revision which contains a known language.',
    )
    parser.add_argument(
        '--only-revisions-with-languages',
        action='store_true',
        help='Consider only the revisions with contain at least a known language.',
    )
    parser.add_argument(
        '--only-last-revision',
        action='store_true',
        help='Consider only the last revision for each page.',
    )
    parser.set_defaults(func=main)


def main(
        dump: Iterable[mwxml.Page],
        features_output_h,
        stats_output_h,
        args) -> None:
    """Main function that parses the arguments and writes the output."""

    stats = {
        'performance': {
            'start_time': None,
            'end_time': None,
            'revisions_analyzed': 0,
            'pages_analyzed': 0,
        },
        'users': {
            'total': 0,                             # total number of users who have declared to know at least one language
            'languages': dict(),                    # dictionary of languages and the level of knowledge associated
            'num_unique_languages': 0,        # total number of different and unique languages known by all analyzed users 
        },
    }

    pages_generator = extract_pages(
        dump,
        stats=stats,
        only_last_revision=args.only_last_revision,
        only_pages_with_languages=args.only_pages_with_languages,
        only_revisions_with_languages=args.only_revisions_with_languages
    )

    stats['performance']['start_time'] = datetime.datetime.utcnow()

    # Number of unique languages known
    print('Ci arrivooooo')
    print(type(stats['users']['languages']))
    print(len(stats['users']['languages']))
    stats['users']['flex'] = len(stats['users']['languages'])

    for obj in pages_generator:
        features_output_h.write(json.dumps(obj.to_dict()))
        features_output_h.write("\n")
    
    stats['performance']['end_time'] = datetime.datetime.utcnow()
    stats_output_h.write(json.dumps(stats, indent=4, default=str))