"""Extract the language known by the registered users in Wikipedia and some statistics about them"""

import collections
import datetime

import more_itertools
import mwxml
import jsonable
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional

from .. import dumper, extractors, languages, utils

# TODO change the check for mother tongue level
features_template = '''
<mediawiki xml:lang="en">
    <siteinfo>
        <sitename>${siteinfo.name | x}</sitename>
        <dbname>${siteinfo.dbname | x}</dbname>
        <base>${siteinfo.base | x}</base>
        <generator>${generator | x}</generator>
        <case>${siteinfo.case | x}</case>
        <namespaces>
            % for namespace in siteinfo.namespaces:
            <namespace key="${namespace.id | x}" case="${namespace.case | x}">${namespace.name | x}</namespace>
            % endfor
        </namespaces>
    </siteinfo>
    % for page in pages:  # basically a for in xml
    <user>
        <title>${page.title | x}</title>
        <ns>${page.namespace | x}</ns>
        <id>${page.id | x}</id>
        % for revision in page.revisions:
        <revision>
            <id>${revision.id | x}</id>
            <user>${revision.user | x}</user>
            <user_id>${revision.user_id | x}</user_id>
            <user_name>${revision.user_name | x}</user_name>
            <timestamp>${revision.timestamp | x}</timestamp>
            <text xml:space="preserve">${revision.text | x}</text>
            <languages>
                % for l in revision.languages:
                <knowledge>
                    <lang>${l.lang | x}</lang>
                    % if l.level == 6: 
                        <level>N</level>
                    % else:
                        <level>${l.level | x}</level>
                    % endif
                </knowledge>
                % endfor
            </languages>
        </revision>
        % endfor
    </user>
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
        <total>${stats['users']['total']| x}</total>
        <languages>
            % for l in stats['users']['languages']:
            <lang>
                <name>${l | x}</name>
                % for i in range(len(stats['users']['languages'][l]['knowledge'])):
                <knowledge>
                    <level>${i| x}</level>
                    <occurences>${stats['users']['languages'][l]['knowledge'][i]| x}<occurences>
                </knowledge>
                % endfor
            </lang>
            % endfor
        </languages>
    </users>
</stats>
'''

Page = collections.namedtuple('Page', [
    'id',
    'namespace',
    'title',
    'revisions',
])

Revision = collections.namedtuple('Revision', [
    'id',
    'user',
    'user_id',
    'user_name',
    'text',          # only for debug purpose
    'timestamp',
    'languages',
])

def extract_revisions(
        mw_page: mwxml.Page,
        stats: Mapping,
        only_last_revision: bool,
        only_revisions_with_languages: bool) -> Iterator[Revision]:
    
    """Extract the known languages within a user's page."""
    revisions = more_itertools.peekable(mw_page)
    
    for mw_revision in revisions:
        utils.dot()

        is_last_revision = not utils.has_next(revisions)
        if only_last_revision and not is_last_revision:
            continue

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

        # Return only the revision's with at least one language
        if only_revisions_with_languages:
            if languages:
                yield Revision(
                    id=mw_revision.id,
                    user=mw_revision.user,
                    user_id=mw_revision.user.id,
                    user_name=mw_revision.user.text,
                    text=text,
                    timestamp=mw_revision.timestamp.to_json(),
                    languages=languages
                )
        else:
            yield Revision(
                id=mw_revision.id,
                user=mw_revision.user,
                user_id=mw_revision.user.id,
                user_name=mw_revision.user.text,
                text=text,
                timestamp=mw_revision.timestamp.to_json(),
                languages=languages
            )
        stats['performance']['revisions_analyzed'] += 1


def extract_pages(
        dump: Iterable[mwxml.Page],
        stats: Mapping,
        only_last_revision: bool,
        only_pages_with_languages: bool,
        only_revisions_with_languages: bool) -> Iterator[Page]:
    """Extract known languages from an user's page."""

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
            only_revisions_with_languages=only_revisions_with_languages,
        )

        if only_pages_with_languages:
            if utils.has_next(more_itertools.peekable(revisions_generator)):
                yield Page(
                    id=mw_page.id,
                    namespace=mw_page.namespace,
                    title=mw_page.title,
                    revisions=revisions_generator,
                )
                stats['users']['total'] += 1
        else:
            yield Page(
                id=mw_page.id,
                namespace=mw_page.namespace,
                title=mw_page.title,
                revisions=revisions_generator,
            )
            stats['users']['total'] += 1
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

    pages_generator = extract_pages(
        dump,
        stats=stats,
        only_last_revision=args.only_last_revision,
        only_pages_with_languages=args.only_pages_with_languages,
        only_revisions_with_languages=args.only_revisions_with_languages,
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