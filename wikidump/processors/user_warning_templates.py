"""Extract the language known by the registered users in Wikipedia and some statistics about them"""

import collections
import json
import more_itertools
import mwxml
import datetime
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional
from backports.datetime_fromisoformat import MonkeyPatch

from .. import dumper, extractors, user_warnings_en, user_warnings_it, user_warnings_es, user_warnings_ca, utils

# Polyfiller for retrocompatibiliy with Python3.5
MonkeyPatch.patch_fromisoformat()

user_warnings_templates = set(
    user_warnings_en.block_templates_indefinitely_blocked_templates + \
    user_warnings_en.block_templates + \
    user_warnings_en.arbitration_enforcement_templates_1RR_related_templates + \
    user_warnings_en.arbitration_enforcement_templates_pages_with_discretionary_sanctions_editnotice + \
    user_warnings_en.arbitration_enforcement_templates + \
    user_warnings_en.csd_warning_templates + \
    user_warnings_en.community_authorised_general_sanctions_templates + \
    user_warnings_en.community_authorised_general_sanctions_templates_standardized + \
    user_warnings_en.community_authorised_general_sanctions_templates_obsolete + \
    user_warnings_en.non_english_welcome + \
    user_warnings_en.non_english + \
    user_warnings_en.test_templates + \
    user_warnings_en.standardized_templates + \
    user_warnings_en.user_warnings_templates + \

    user_warnings_it.avviso_utenti_anonimi + \
    user_warnings_it.benvenuto + \
    user_warnings_it.benvenuto_progetti + \
    user_warnings_it.avviso_copyright + \
    user_warnings_it.avviso_invito_progetti + \
    user_warnings_it.vandalismo + \

    user_warnings_es.bienvenida + \
    user_warnings_es.permission_grant_notification_templates + \
    user_warnings_es.user_warnings + \

    user_warnings_ca.benvinguda + \
    user_warnings_ca.Avisos_de_discussio + \
    user_warnings_ca.plantilles_d_avisos_d_edicio_generics + \
    user_warnings_ca.plantilles_d_avisos_d_edicio + \
    user_warnings_ca.plantilles_d_avisos_d_idioma + \
    user_warnings_ca.plantilles_d_avisos 
)

# REVISION AND PAGE CLASSES
class Revision:
    """Class which represent a revision of the template page"""
    def __init__(self, id: str, user: mwxml.Revision.User, text: str, timestamp: str, templates: extractors.user_warnings_template.UserWarningTemplate):
        self.id = id                                                # revision id
        self.user = user                                            # revision user
        self.timestamp = timestamp                                  # revision timestamp
        self.text = text                                            # revision text
        self.templates = templates                                  # list of regex for that particular template and the parameters of that template

    def to_dict(self) -> str:
        """Converts the object instance into a dictionary"""
        obj = dict()
        obj['id'] = self.id
        user_id = ''
        user_name = ''
        if self.user:
            user_id = self.user.id
            user_name = self.user.text
        obj['user_id'] = user_id
        obj['user_name'] = user_name
        obj['timestamp'] = self.timestamp
        obj['text'] = self.text
        obj['templates'] = self.templates.to_dict()
        return obj

class Page:
    """Class which represent a page containing a list of revisions"""
    def __init__(self, id: str, namespace: str, title: str, revisions: Iterator[Revision]):
        self.id = id                            # page id
        self.namespace = namespace              # page namespace
        self.title = title                      # page title
        self.revisions = revisions              # list of revisions

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
        only_last_revision: bool) -> Iterator[Revision]:
    
    """Extracts the history of a user_warning_template within a template page."""
    revisions = more_itertools.peekable(mw_page)

    # Newest revisions, useful only if the only_last_revision flag is set equal to true
    newest_revision = None

    for mw_revision in revisions:
        utils.dot()

        # check if it's last revision
        is_last_revision = not utils.has_next(revisions)

        # remove html comments
        text = utils.remove_comments(mw_revision.text or '')

        templates = extractors.user_warnings_template.userwarnings_regex_extractor(text)

        # Build the revision
        rev = Revision(
            id=mw_revision.id,
            user=mw_revision.user,
            text=text,
            timestamp=mw_revision.timestamp.to_json(),
            templates=templates,
        )

        # TODO revisions need to be more accurate, excecially their change date

        # Check the oldest revisions possible
        if not newest_revision:
            newest_revision = rev
        else:
            newest_date = datetime.datetime.fromisoformat(newest_revision.timestamp.replace('Z', '+00:00'))
            current_date = datetime.datetime.fromisoformat(mw_revision.timestamp.to_json().replace('Z', '+00:00'))
            # change the revision if the current one is newer
            if newest_date < current_date:
                newest_revision = rev

        # Update stats
        stats['performance']['revisions_analyzed'] += 1
        stats['templates']['stats'][mw_page.title]['revisions'] += 1
        stats['templates']['stats'][mw_page.title]['last_revision_date'] = datetime.datetime.fromisoformat(newest_revision.timestamp.replace('Z', '+00:00'))
        stats['templates']['stats'][mw_page.title]['revision_changes'].append(datetime.datetime.fromisoformat(mw_revision.timestamp.to_json().replace('Z', '+00:00')))
        stats['templates']['stats'][mw_page.title]['not_modified_since'] =  datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(newest_revision.timestamp.replace('Z', '+00:00'))

        # requested only the last revision
        if only_last_revision:
            if is_last_revision:
                yield newest_revision
        else:
            yield rev

def extract_pages(
        dump: Iterable[mwxml.Page],
        stats: Mapping,
        only_last_revision: bool) -> Iterator[Page]:
    """Extract the templates from an user page."""

    # Loop on all the pages in the dump, one at a time
    for mw_page in dump:
        utils.log("Processing", mw_page.title)
        
        # Skip non-template, according to https://en.wikipedia.org/wiki/Wikipedia:Namespace
        if mw_page.namespace != 10 or not mw_page.title.lower() in user_warnings_templates:
            utils.log('Skipped (namespace != 10 or different template from the user warnings ones)')
            continue
    
        # create the stats needed
        stats['templates']['stats'][mw_page.title] = dict()
        stats['templates']['stats'][mw_page.title]['revisions'] = 0
        stats['templates']['stats'][mw_page.title]['last_revision_date'] = None
        stats['templates']['stats'][mw_page.title]['revision_changes'] = list()
        stats['templates']['stats'][mw_page.title]['average_modification_time'] = 0
        stats['templates']['stats'][mw_page.title]['not_modified_since'] = None

        revisions_generator = extract_revisions(
            mw_page,
            stats=stats,
            only_last_revision=only_last_revision
        )

        revisions_list = list(revisions_generator)

        page = Page(
            id=mw_page.id,
            namespace=mw_page.namespace,
            title=mw_page.title,
            revisions=revisions_list,
        )

        # stats update
        stats['templates']['total'] += 1
        stats['templates']['stats'][mw_page.title]['revision_changes'].sort()
        # calculate the average average_modification_time
        for index in range(1, len(stats['templates']['stats'][mw_page.title]['revision_changes'])):
            old = stats['templates']['stats'][mw_page.title]['revision_changes'][index - 1]
            new = stats['templates']['stats'][mw_page.title]['revision_changes'][index]
            stats['templates']['stats'][mw_page.title]['average_modification_time'] += (new - old).total_seconds()

        # for now they are seconds
        stats['templates']['stats'][mw_page.title]['average_modification_time'] /=  stats['templates']['stats'][mw_page.title]['revisions']
        stats['templates']['stats'][mw_page.title]['average_modification_time'] = str(datetime.timedelta(seconds = stats['templates']['stats'][mw_page.title]['average_modification_time']))

        yield page

        break

        stats['performance']['pages_analyzed'] += 1

def configure_subparsers(subparsers):
    """Configure a new subparser for the known languages."""
    parser = subparsers.add_parser(
        'extract-user-warnings-templates',
        help='Extract the history of the templates of the users warnings',
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
        'templates': {
            'total': 0,  # total number of templates analyzed
            'amount_of_user_warnings:': len(user_warnings_templates),
            'stats': dict() # stats per template
        },
    }

    pages_generator = extract_pages(
        dump,
        stats=stats,
        only_last_revision=args.only_last_revision
    )

    stats['performance']['start_time'] = datetime.datetime.utcnow()

    for obj in pages_generator:
        features_output_h.write(json.dumps(obj.to_dict(), indent=4))
        features_output_h.write("\n")
    
    stats['performance']['end_time'] = datetime.datetime.utcnow()
    stats_output_h.write(json.dumps(stats, indent=4, default=str))