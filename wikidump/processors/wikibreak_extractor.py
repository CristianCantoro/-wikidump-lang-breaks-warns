"""Extract the the wikibreaks option in the user page and user talk page"""

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
    def __init__(self, id: str, user: mwxml.Revision.User, timestamp: str, wikibreaks: Iterable[extractors.wikibreaks.Wikibreak], 
        num_wikibreaks: int, at_least_one_parameter: bool, template_occurences: Mapping):
        self.id = id                                                # revision id
        self.user = user                                            # revision user
        self.timestamp = timestamp                                  # revision timestamp
        self.wikibreaks = wikibreaks                                # set of wikibreaks
        self.num_wikibreaks = num_wikibreaks                        # number of wikibreaks
        self.at_least_one_parameter = at_least_one_parameter        # boolean value which tells if contains a wikibreak with at least a parameter
        self.template_occurences = template_occurences              # categories and subcategories of the templates used and a boolean value if they have parameters or not

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
        obj['wikibreaks'] = list()
        for w_b in self.wikibreaks:
            print('Sto leggenedo:', w_b)
            obj['wikibreaks'].append(w_b.to_dict())
        return obj

class Page:
    """Class which represent a page containing a list of revisions"""
    def __init__(self, id: str, namespace: str, title: str, revisions: Iterator[Revision], num_wikibreaks: int):
        self.id = id                            # page id
        self.namespace = namespace              # page namespace
        self.title = title                      # page title
        self.revisions = revisions              # list of revisions
        self.num_wikibreaks = num_wikibreaks    # number of wikibreaks

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
    
    """Extracts the wikibreaks within a user page or user talk page."""
    revisions = more_itertools.peekable(mw_page)

    # Newest revisions, useful only if the only_last_revision flag is set equal to true
    newest_revision = None

    for mw_revision in revisions:
        utils.dot()

        # check if it's last revision
        is_last_revision = not utils.has_next(revisions)

        # remove html comments
        text = utils.remove_comments(mw_revision.text or '')

        # It extracts a the wikibreak name and its parameters
        wikibreaks = list()
        at_least_one_parameter_template_counter = 0      # number of parametrized templates
        template_occurences = dict()                     # template category and subcategory and if they have a parameter or not

        for wikibreak, _ in extractors.wikibreaks.wikibreaks_extractor(text):
            wikibreaks.append(wikibreak)
            at_least_one_parameter_template_counter += int(wikibreak.at_least_one_parameter)    # count the number of parametrized templates
            for category in wikibreak.wikibreak_category:
                if not category in template_occurences:
                    template_occurences[category] = { 'at_least_a_parameter': False, 'is_category': True} # add the category
                # save the category and if they come at least one time parametrized
                template_occurences[category]['at_least_a_parameter'] = template_occurences[category]['at_least_a_parameter'] or wikibreak.at_least_one_parameter   
            if not wikibreak.wikibreak_subcategory in template_occurences:
                template_occurences[wikibreak.wikibreak_subcategory] = { 'at_least_a_parameter': False, 'is_category': False }
            # save the subcategory and if they come at least one time parametrized
            template_occurences[wikibreak.wikibreak_subcategory]['at_least_a_parameter']= template_occurences[wikibreak.wikibreak_subcategory]['at_least_a_parameter'] or wikibreak.at_least_one_parameter

        # Update stats
        stats['wikibreaks']['templates'] += len(wikibreaks)
        stats['wikibreaks']['templates_at_least_one_parameter'] += at_least_one_parameter_template_counter

        # Build the revision
        rev = Revision(
            id=mw_revision.id,
            user=mw_revision.user,
            timestamp=mw_revision.timestamp.to_json(),
            wikibreaks=wikibreaks,
            num_wikibreaks=len(wikibreaks),
            at_least_one_parameter=(at_least_one_parameter_template_counter > 0),
            template_occurences=template_occurences
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
            # asked for revisions with wikibreaks
            if only_revisions_with_wikibreaks:
                # has the wikibreaks list not empty
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
        if mw_page.namespace != 2 and mw_page.namespace != 3:
            utils.log('Skipped (namespace != 2 and namespace != 3)')
            continue

        revisions_generator = extract_revisions(
            mw_page,
            stats=stats,
            only_last_revision=only_last_revision,
            only_revisions_with_wikibreaks=only_revisions_with_wikibreaks
        )

        revisions_list = list(revisions_generator)

        num_wikibreaks = 0  # number of wikibreaks
        users_at_least_parameter = False    # the user has at least a template with at least a parameter
        categories_occurences = dict()      # categories and subcategories dictionary. It contains the number of user who have used them and the number of user who have used them with at leas a parameter
        for rev in revisions_list:
            # number of wikibreaks
            num_wikibreaks += rev.num_wikibreaks
            # if this is a user who have been in wikipause and has specified the 
            users_at_least_parameter = users_at_least_parameter or rev.at_least_one_parameter
            # update stats related to the occurrences of a category or a template (calculated per user)
            for category in rev.template_occurences:
                if not category in categories_occurences:
                    categories_occurences[category] = {'total': False, 'with_params': False, 'is_category': rev.template_occurences[category]['is_category']}
                # total number of users who have been on wikibreak using that wikibreak category at least once 
                categories_occurences[category]['total'] = True          
                # total number of users who have been on wikibreak using that wikibreak category at least once with at least a parameter                                                                                   
                categories_occurences[category]['with_params'] = categories_occurences[category]['with_params'] or rev.template_occurences[category]['at_least_a_parameter']

        page = Page(
            id=mw_page.id,
            namespace=mw_page.namespace,
            title=mw_page.title,
            revisions=revisions_list,
            num_wikibreaks=num_wikibreaks
        )
        
        # stats update
        stats['wikibreaks']['users_at_least_parameter'] += int(users_at_least_parameter)
        for category in categories_occurences:
            if categories_occurences[category]['is_category']:
                if not category in stats['wikibreaks']['user_categories_occurences']:
                    stats['wikibreaks']['user_categories_occurences'][category] = {'total': False, 'with_params': False}
                stats['wikibreaks']['user_categories_occurences'][category]['total'] += int(categories_occurences[category]['total'])
                stats['wikibreaks']['user_categories_occurences'][category]['with_params'] += int(categories_occurences[category]['with_params'])
            else:
                if not category in stats['wikibreaks']['user_subcategories_occurences']:
                    stats['wikibreaks']['user_subcategories_occurences'][category] = {'total': False, 'with_params': False}
                stats['wikibreaks']['user_subcategories_occurences'][category]['total'] += int(categories_occurences[category]['total'])
                stats['wikibreaks']['user_subcategories_occurences'][category]['with_params'] += int(categories_occurences[category]['with_params'])

        # Return only the pages with at least one wikibreak if the flag's active
        if only_pages_with_wikibreaks:
            if page.num_wikibreaks > 0:
                stats['wikibreaks']['users'] += 1
                yield page
        else:
            if page.num_wikibreaks > 0:
                stats['wikibreaks']['users'] += 1
            yield page
    
        stats['performance']['pages_analyzed'] += 1

def configure_subparsers(subparsers):
    """Configure a new subparser for the known languages."""
    parser = subparsers.add_parser(
        'extract-wikibreaks',
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
            'users': 0,                                 # users that have specified a wikibreak or other similiar templates at least one time during their wikilife
            'users_at_least_parameter': 0,              # users that have specified a wikibreak or other similar templates least one time during their wikilife with at least one parameter
            'templates': 0,                             # wikibreaks or similar templates encountered, in any revision of any user
            'templates_at_least_one_parameter': 0,      # wikibreaks or similar templates encountered, in any revision of any user, with at least one parameter
            'user_categories_occurences': dict(),       # category dictionary. It contains the number of user who have used them and the number of user who have used them with at leas a parameter
            'user_subcategories_occurences': dict(),    # subcategories dictionary. It contains the number of user who have used them and the number of user who have used them with at leas a parameter
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