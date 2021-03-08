"""Extract the language known by the registered users in Wikipedia and some statistics about them"""

import collections
import datetime

import more_itertools
import mwxml
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional

from .. import dumper, extractors, languages, utils

# TODO define which feature I want to be extracted from the user pages
features_template = '''
'''

stats_template = '''
<stats>
    <performance>
        <start_time>${stats['performance']['start_time']}</start_time>
        <end_time>${stats['performance']['end_time']}</end_time>
        <revisions_analyzed>${stats['performance']['revisions_analyzed']}</revisions_analyzed>
        <pages_analyzed>${stats['performance']['pages_analyzed']}</pages_analyzed>
    </performance>
    <identifiers>
        TODO define
    </identifiers>
</stats>
'''

# TODO define
Page = collections.namedtuple('Page', [
    'id',
    'title',
    'revisions',
])

# TODO define
Revision = collections.namedtuple('Revision', [
    'id',
    'user',
    'timestamp',
])


def extract_revisions(
        mw_page: mwxml.Page,
        language: str,
        stats: Mapping,
        only_last_revision: bool) -> Iterator[Revision]:
    """Extract the known languages within a user's page."""
    section_names_stats = stats['section_names']
    revisions = more_itertools.peekable(mw_page)
    for mw_revision in revisions:
        utils.dot()
        pass


def extract_pages(
        dump: Iterable[mwxml.Page],
        stats: Mapping,
        only_last_revision: bool) -> Iterator[Page]:
    """Extract revisions from a page."""
    for mw_page in dump:
        pass


def configure_subparsers(subparsers):
    """Configure a new subparser for the known languages."""
    parser = subparsers.add_parser(
        'extract-known-languages',
        help='Extract the languages known by the users',
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
        'section_names': {
            'global': collections.Counter(),
            'last_revision': collections.Counter(),
        },
    }

    pages_generator = extract_pages(
        dump,
        stats=stats,
        only_last_revision=args.only_last_revision,
    )

    with features_output_h:
        stats['performance']['start_time'] = datetime.datetime.utcnow()
        dumper.render_template(
            features_template,
            output_handler=features_output_h,
            siteinfo=dump.site_info,
            pages=pages_generator,
            generator='youtux/wikidump',
        )
        stats['performance']['end_time'] = datetime.datetime.utcnow()

    with stats_output_h:
        dumper.render_template(
            stats_template,
            stats_output_h,
            stats=stats,
        )