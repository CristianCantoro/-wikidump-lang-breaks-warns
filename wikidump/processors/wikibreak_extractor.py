"""Extract the language known by the registered users in Wikipedia and some statistics about them"""

import collections
import json
import more_itertools
import mwxml
import datetime
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional
from backports.datetime_fromisoformat import MonkeyPatch

from .. import dumper, extractors, wikibreaks, utils

# Polyfiller for retrocompatibiliy with Python3.5
MonkeyPatch.patch_fromisoformat()

# REVISION AND PAGE CLASSES
class Revision:
    """Class which represent a revision of the user page"""
    def __init__(self, id: str, user: mwxml.Revision.User, timestamp: str, text: str, wikibreaks: Iterable[extractors.wikibreaks.Wikibreak]):
        self.id = id                    # revision id
        self.user = user                # revision user
        self.timestamp = timestamp      # revision timestamp
        self.text = text                # revision text content
        self.wikibreaks = wikibreaks    # set of wikibreaks

    def to_dict(self) -> str:
        """Converts the object instance into a dictionary"""
        obj = dict()
        obj['id'] = self.id
        obj['user_id'] = self.user.id
        obj['user_name'] = self.user.text
        obj['timestamp'] = self.timestamp
        obj['text'] = self.text
        obj['wikibreaks'] = list()
        for w_b in self.wikibreaks:
            obj['wikibreaks'].append(w_b.to_dict())
        return obj

class Page:
    """Class which represent a page containing a list of revisions"""
    def __init__(self, id: str, namespace: str, title: str, revisions: Iterator[Revision]):
        self.id = id                # page id
        self.namespace = namespace  # page namespace
        self.title = title          # page title
        self.revisions = revisions  # list of revisions

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

def extract_revisions(
        mw_page: mwxml.Page,
        stats: Mapping,
        only_last_revision: bool,
        only_revisions_with_wikibreaks: bool) -> Iterator[Revision]:
    
    """Extracts the known languages within a user page or user talk page."""
    revisions = more_itertools.peekable(mw_page)

    # Newest revisions, useful only if the only_last_revision flag is set equal to true
    newest_revision = None

    for mw_revision in revisions:
        utils.dot()

        # check if it's last revision
        is_last_revision = not utils.has_next(revisions)

        # remove html comments
        text = utils.remove_comments(mw_revision.text or '')

        # It extracts a TODO about wikibreks
        wikibreaks = [wikibreak for wikibreak, _ in extractors.wikibreaks.wikibreaks_extractor(text)]

        # Update stats
        for wb in wikibreaks:
            # TODO Update stats if necessary
            pass

        # Build the revision
        rev = Revision(
            id=mw_revision.id,
            user=mw_revision.user,
            timestamp=mw_revision.timestamp.to_json(),
            text=mw_revision.text,
            wikibreaks=wikibreaks
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
            if only_revisions_with_wikibreaks:
                # has the languages list not empty
                if newest_revision.wikibreaks and is_last_revision:
                    yield newest_revision
            elif is_last_revision:
                yield newest_revision
        elif only_revisions_with_wikibreaks:
            if wikibreaks:
                yield rev
        else:
            yield rev

def extract_pages(
        dump: Iterable[mwxml.Page],
        stats: Mapping,
        only_last_revision: bool,
        only_pages_with_wikibreaks: bool,
        only_revisions_with_wikibreaks: bool) -> Iterator[Page]:
    """Extract wikibreaks from an user page."""

    # Loop on all the pages in the dump, one at a time
    for mw_page in dump:
        utils.log("Processing", mw_page.title)
        
        # Skip non-(user pages or ser talk page), according to https://en.wikipedia.org/wiki/Wikipedia:Namespace
        if mw_page.namespace != 2:
            utils.log('Skipped (namespace != 2)')
            continue
        elif mw_page.namespace != 3:
            utils.log('Skipped (namespace != 3)')
            continue
        
        revisions_generator = extract_revisions(
            mw_page,
            stats=stats,
            only_last_revision=only_last_revision,
            only_revisions_with_wikibreaks=only_revisions_with_wikibreaks
        )

        page = Page(
            id=mw_page.id,
            namespace=mw_page.namespace,
            title=mw_page.title,
            revisions=list(revisions_generator),
        )

        # Return only the pages with at least one wikibreak if the flag's active
        if only_pages_with_wikibreaks:
            if len(page.revisions) > 0:
                stats['wikibreaks']['total'] += 1
                yield page
        else:
            stats['wikibreaks']['total'] += 1
            yield page
            
        if stats['wikibreaks']['total'] == 10:
            break
        
        stats['performance']['pages_analyzed'] += 1

def configure_subparsers(subparsers):
    """Configure a new subparser for the known languages."""
    parser = subparsers.add_parser(
        'extractor_wikibreaks',
        help='Extract the languages known by the users',
    )
    parser.add_argument(
        '--only-pages-with-wikibreaks',
        action='store_true',
        help='Consider only the pages with at least a revision which contains a wikibreak.',
    )
    parser.add_argument(
        '--only-revisions-with-wikibreaks',
        action='store_true',
        help='Consider only the revisions with contain at least a wikibreak.',
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
        'wikibreaks': {
            'total': 0,
        },
    }

    pages_generator = extract_pages(
        dump,
        stats=stats,
        only_last_revision=args.only_last_revision,
        only_pages_with_wikibreaks=args.only_pages_with_wikibreaks,
        only_revisions_with_wikibreaks=args.only_revisions_with_wikibreaks
    )

    stats['performance']['start_time'] = datetime.datetime.utcnow()

    for obj in pages_generator:
        features_output_h.write(json.dumps(obj.to_dict(), indent=4))
        features_output_h.write("\n")
    
    stats['performance']['end_time'] = datetime.datetime.utcnow()
    stats_output_h.write(json.dumps(stats, indent=4, default=str))
    stats_output_h.write("\n")