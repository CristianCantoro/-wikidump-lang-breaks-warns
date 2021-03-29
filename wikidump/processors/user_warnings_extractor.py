"""Extract the user warnings templates and the options specified in user talk pages"""

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
    def __init__(self, id: str, user: mwxml.Revision.User, timestamp: str, user_warnings: Iterable[extractors.user_warnings.UserWarning], 
        num_user_warnings: int, at_least_one_parameter: bool):
        self.id = id                                                # revision id
        self.user = user                                            # revision user
        self.timestamp = timestamp                                  # revision timestamp
        self.user_warnings = user_warnings                          # set of user warnings
        self.num_user_warnings = num_user_warnings                  # number of user warnings
        self.at_least_one_parameter = at_least_one_parameter        # boolean value which tells if contains an user warnings with at least a parameter

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
        obj['user_warnings'] = list()
        for u_w in self.user_warnings:
            obj['user_warnings'].append(u_w.to_dict())
        return obj

class Page:
    """Class which represent a page containing a list of revisions"""
    def __init__(self, id: str, namespace: str, title: str, revisions: Iterator[Revision], num_user_warnings: int):
        self.id = id                                    # page id
        self.namespace = namespace                      # page namespace
        self.title = title                              # page title
        self.revisions = revisions                      # list of revisions
        self.num_user_warnings = num_user_warnings      # number of user warnings

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
        only_revisions_with_user_warnings: bool) -> Iterator[Revision]:
    
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

        # It extracts a the user warning name and its parameters
        user_warnings = list()
        at_least_one_parameter_template_counter = 0      # number of parametrized templates

        # populate the list of user warnings and count how many templates have at least a parameter
        for user_w, _ in extractors.user_warnings.user_warnings_extractor(text):
            user_warnings.append(user_w)
            at_least_one_parameter_template_counter += int(user_w.at_least_one_parameter)    # user has at least a parametrized user warnings templates

        # Update stats
        stats['user_warnings']['templates'] += len(user_warnings)
        stats['user_warnings']['templates_at_least_one_parameter'] += at_least_one_parameter_template_counter

        # Build the revision
        rev = Revision(
            id=mw_revision.id,
            user=mw_revision.user,
            timestamp=mw_revision.timestamp.to_json(),
            user_warnings=user_warnings,
            num_user_warnings=len(user_warnings),
            at_least_one_parameter=(at_least_one_parameter_template_counter > 0),
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
            # asked for revisions with user warnings
            if only_revisions_with_user_warnings:
                # has the user warning list not empty
                if newest_revision.user_warnings and is_last_revision:
                    yield newest_revision
            elif is_last_revision:
                yield newest_revision
        elif only_revisions_with_user_warnings:
            if user_warnings:
                yield rev
        else:
            yield rev

def extract_pages(
        dump: Iterable[mwxml.Page],
        stats: Mapping,
        only_last_revision: bool,
        only_pages_with_user_warnings: bool,
        only_revisions_with_user_warnings: bool) -> Iterator[Page]:
    """Extract user warnings from an user page."""

    # Loop on all the pages in the dump, one at a time
    for mw_page in dump:
        utils.log("Processing", mw_page.title)
        
        # Skip non-user talk page, according to https://en.wikipedia.org/wiki/Wikipedia:Namespace
        if mw_page.namespace != 3:
            utils.log('Skipped namespace != 3')
            continue
        
        revisions_generator = extract_revisions(
            mw_page,
            stats=stats,
            only_last_revision=only_last_revision,
            only_revisions_with_user_warnings=only_revisions_with_user_warnings
        )

        # list of revisions
        revisions_list = list(revisions_generator)

        num_user_warnings = 0               # number of user warnings totally encountered
        users_at_least_parameter = False    # the user has at least a template with at least a parameter
        template_occurences = dict()        # template dictionary, template which contains each template and the number of users who have it in their user talk page and the number
                                            # of user who have it in their talk page with at least a parameter
        for rev in revisions_list:
            # number of user warnings
            num_user_warnings += rev.num_user_warnings
            # have at least a user warnings with a parameter
            users_at_least_parameter = users_at_least_parameter or rev.at_least_one_parameter
            # update stats related to the the template, if it is present at least one time in the user talk page and if it have ever had a parameter
            for u_w in rev.user_warnings:
                if not u_w.user_warning_name in template_occurences:
                    template_occurences[u_w.user_warning_name] = {'total': False, 'with_params': False, 'lang': u_w.lang}
                # it has occurred
                template_occurences[u_w.user_warning_name]['total'] = True          
                # it has occurred with at least a parameter                                                                                   
                template_occurences[u_w.user_warning_name]['with_params'] = template_occurences[u_w.user_warning_name]['with_params'] or u_w.at_least_one_parameter

        page = Page(
            id=mw_page.id,
            namespace=mw_page.namespace,
            title=mw_page.title,
            revisions=revisions_list,
            num_user_warnings=num_user_warnings
        )

        # stats update
        stats['user_warnings']['users_at_least_parameter'] += int(users_at_least_parameter)
        for u_w in template_occurences:
            lang = template_occurences[u_w]['lang']
            if lang not in stats['user_warnings']['user_template_occurences']:
                # all the templates in that language are inserted with 0 occurences and 0 occurences with paramters
                stats['user_warnings']['user_template_occurences'][lang] = dict()
                for template in extractors.user_warnings.lang_dict[lang]:
                    stats['user_warnings']['user_template_occurences'][lang][template] = { 'user_talk_occurences': 0, 'user_talk_occurences_with_params': 0 }
            # the user had or have that template with or without paramters
            stats['user_warnings']['user_template_occurences'][lang][u_w]['user_talk_occurences'] += int(template_occurences[u_w]['total'])
            stats['user_warnings']['user_template_occurences'][lang][u_w]['user_talk_occurences_with_params'] += int(template_occurences[u_w]['with_params'])

         
        # Return only the pages with at least one user warning if the flag's active
        if only_pages_with_user_warnings:
            if page.num_user_warnings > 0:
                stats['user_warnings']['users'] += 1
                yield page
        else:
            if page.num_user_warnings > 0:
                stats['user_warnings']['users'] += 1
            yield page

        stats['performance']['pages_analyzed'] += 1

def configure_subparsers(subparsers):
    """Configure a new subparser for the known languages."""
    parser = subparsers.add_parser(
        'extract-user-warnings',
        help='Extract the user warnings information of the transcluded templates',
    )
    parser.add_argument(
        '--only-pages-with-user-warnings',
        action='store_true',
        help='Consider only the pages with at least an user warning.',
    )
    parser.add_argument(
        '--only-revisions-with-user-warnings',
        action='store_true',
        help='Consider only the revisions with contain at least an user warning.',
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
        'user_warnings': {
            'users': 0,                                 # users that have at least a user warning in their talk page
            'users_at_least_parameter': 0,              # users that have at least a user warning in their talk page with at least one parameter
            'templates': 0,                             # user warnings or similar templates encountered, in any revision of any user
            'templates_at_least_one_parameter': 0,      # user warnings templates encountered, in any revision of any user, with at least one parameter
            'user_template_occurences': dict(),         # template dictionary. It contains the number of user who have used them and the number of user who have used them with at least a parameter
        },
    }

    pages_generator = extract_pages(
        dump,
        stats=stats,
        only_last_revision=args.only_last_revision,
        only_pages_with_user_warnings=args.only_pages_with_user_warnings,
        only_revisions_with_user_warnings=args.only_revisions_with_user_warnings
    )

    stats['performance']['start_time'] = datetime.datetime.utcnow()

    for obj in pages_generator:
        features_output_h.write(json.dumps(obj.to_dict()))
        features_output_h.write("\n")
    
    stats['performance']['end_time'] = datetime.datetime.utcnow()
    stats_output_h.write(json.dumps(stats, indent=4, default=str))