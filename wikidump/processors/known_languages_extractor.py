"""Extract the language known by the registered users in Wikipedia and some statistics about them"""

import collections
import datetime
import json
import more_itertools
import mwxml
import datetime
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional

from .. import dumper, extractors, languages, utils

# GENERATORS CONSUMES

class Page:
    def __init__(self, id, namespace, title, revisions):
        self.id = id
        self.namespace = namespace
        self.title = title
        self.revisions = revisions
        self.discard = False

    def to_dict(self):
        obj = dict()
        obj['id'] = self.id
        obj['namespace'] = self.namespace
        obj['title'] = self.title
        obj['revisions'] = list()
        for rev in self.revisions:
            obj['revisions'].append(rev.to_dict())
        return obj


class Revision:
    def __init__(self, id, user, timestamp, languages):
        self.id = id
        self.user = user
        self.timestamp = timestamp
        self.languages = languages
        self.discard = False

    def to_dict(self):
        obj = dict()
        obj['id'] = self.id
        obj['user_id'] = self.user.id
        obj['user_name'] = self.user.text
        obj['timestamp'] = self.timestamp
        obj['languages'] = list()
        for lang in self.languages:
            obj['languages'].append(lang.to_dict())
        return obj

def extract_revisions(
        mw_page: mwxml.Page,
        stats: Mapping,
        only_last_revision: bool,
        only_revisions_with_languages: bool) -> Iterator[Revision]:
    
    """Extract the known languages within a user's page."""
    revisions = more_itertools.peekable(mw_page)

    oldest_revision = None

    for mw_revision in revisions:
        utils.dot()

        # check if it's last revision
        is_last_revision = not utils.has_next(revisions)

        text = utils.remove_comments(mw_revision.text or '')

        # It extracts a list of LanguageLevel instances, composed of (languages and it's level)
        languages = [lang for lang, _ in extractors.languages.language_knowledge(text)]

        # Update stats
        for l in languages:
            if l.lang in stats['users']['languages']:
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
            languages=languages
        )

        # Check the oldest revisions possible
        if not oldest_revision:
            oldest_revision = rev
        else:
            oldest_date = datetime.datetime.fromisoformat(oldest_revision.timestamp.replace('Z', '+00:00'))
            new_date = datetime.datetime.fromisoformat(mw_revision.timestamp.to_json().replace('Z', '+00:00'))

            # I am interested in only the ones with at least a language
            if only_revisions_with_languages:
                if not languages:
                    new_date = oldest_date

            if oldest_date < new_date:
                oldest_revision = rev

        # Return only the revisions with at least one language if the flag's active
        stats['performance']['revisions_analyzed'] += 1
        
        # Yield when requested
        if only_last_revision:
            if only_revisions_with_languages:
                if oldest_revision.languages and is_last_revision:
                    yield oldest_revision
            elif is_last_revision:
                yield oldest_revision
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
    """Extract known languages from an user's page."""

    break_me_counter = 50

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

        page = Page(
            id=mw_page.id,
            namespace=mw_page.namespace,
            title=mw_page.title,
            revisions=list(revisions_generator),
        )

        # Return only the pages with at least one language if the flag's active
        if only_pages_with_languages:
            if len(page.revisions) > 0:
                stats['users']['total'] += 1
                yield page
        else:
            stats['users']['total'] += 1
            yield page

        if mw_page.title == 'Llull':
            break

        stats['performance']['pages_analyzed'] += 1

        break_me_counter -= 1

        if(break_me_counter == 0):
            break

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
        help='Consider only the revisions with contain at a known language.',
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
            'total': 0,
            'languages': dict(),
        },
    }

    print(args.only_last_revision, args.only_pages_with_languages, args.only_revisions_with_languages)

    pages_generator = extract_pages(
        dump,
        stats=stats,
        only_last_revision=args.only_last_revision,
        only_pages_with_languages=args.only_pages_with_languages,
        only_revisions_with_languages=args.only_revisions_with_languages
    )

    stats['performance']['start_time'] = datetime.datetime.utcnow()

    for obj in pages_generator:
        if not obj.discard:
            features_output_h.write(json.dumps(obj.to_dict(), indent=4))
            features_output_h.write("\n")
    
    stats['performance']['end_time'] = datetime.datetime.utcnow()
    stats_output_h.write(json.dumps(stats, indent=4, default=str))
    stats_output_h.write("\n")