"""Extract the language known by the registered users in Wikipedia and some statistics about them"""

import collections
import datetime

import more_itertools
import mwxml
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional

from .. import dumper, extractors, languages, utils

# TODO REMEMBER USER NAMESPACE = 2, define the extractor of the language and the user knowledge
# I need also to better understand how those feautures template work, so it is important to visit: https://docs.makotemplates.org/en/latest/usage.html
# The features and the stats should be compliant with what I've stated in the todo.md file

# TODO define which feature I want to be extracted from the user pages
features_template = '''
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://github.com/youtux/wikidump/blob/master/schemas/wikidump-0.1-mediawiki-0.10.xsd" version="0.10" xml:lang="en">
    % for page in pages:
    <page>
        <title>${page.title | x}</title>
        <ns>${page.namespace | x}</ns>
        <id>${page.id | x}</id>
        % for revision in page.revisions:
        <revision>
            <id>${revision.id | x}</id>
            <user>${revision.user | x}</user>
            <text xml:space="preserve">${revision.text | x}</text>
        </revision>
        % endfor
    </page>
    % endfor
</mediawiki>
'''

stats_template = '''
<stats>
    <performance>
        <start_time>${stats['performance']['start_time']}</start_time>
        <end_time>${stats['performance']['end_time']}</end_time>
        <revisions_analyzed>${stats['performance']['revisions_analyzed']}</revisions_analyzed>
        <pages_analyzed>${stats['performance']['pages_analyzed']}</pages_analyzed>
    </performance>
    <users>
        # TODO define
    </users>
</stats>
'''

# TODO define
Page = collections.namedtuple('Page', [
    'id',
    'namespace',
    'title',
    'revisions',
])

# TODO define
Revision = collections.namedtuple('Revision', [
    'id',
    'user',
    'text',     # NOTE: only for now, here are stored all the info in the user's page, so there is the Babel tag we need
])

def extract_revisions(
        mw_page: mwxml.Page,
        stats: Mapping,
        only_last_revision: bool) -> Iterator[Revision]:
    """Extract the known languages within a user's page."""
    revisions = more_itertools.peekable(mw_page)
    for mw_revision in revisions:
        utils.dot()

        text = utils.remove_comments(mw_revision.text or '')

        # languages = (lang for lang, _ in extractors.languages.language_knowledge(text))

        yield Revision(
            id=mw_revision.id,
            user=mw_revision.user,
            text=text,
        )

        stats['performance']['revisions_analyzed'] += 1


def extract_pages(
        dump: Iterable[mwxml.Page],
        stats: Mapping,
        only_last_revision: bool) -> Iterator[Page]:
    """Extract known languages from an user's page."""
    # break after 100 users, this is only for testing
    break_me_counter = 100

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
        )

        yield Page(
            id=mw_page.id,
            namespace=mw_page.namespace,
            title=mw_page.title,
            revisions=revisions_generator,
        )
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
    # to modify
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