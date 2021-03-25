"""Extract the most recurrent tokens of the template text"""

import collections
import json
import more_itertools
import mwxml
import datetime
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional
from backports.datetime_fromisoformat import MonkeyPatch
# nltk
import nltk.corpus 
from nltk.text import TextCollection
from .. import dumper, extractors, user_warnings_en, user_warnings_it, user_warnings_es, user_warnings_ca, utils
import math

# Polyfiller for retrocompatibiliy with Python3.5
MonkeyPatch.patch_fromisoformat()

# time interval in seconds
time_interval_in_seconds = {
    '1 day': 86400,
    '1 week': 604800
}

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
    def __init__(self, id: str, user: mwxml.Revision.User, text: str, timestamp: str, template_info: extractors.user_warnings_template_words.UserWarningTf):
        self.id = id                                                # revision id
        self.user = user                                            # revision user
        self.timestamp = timestamp                                  # revision timestamp
        self.text = text                                            # revision text
        self.template_info = template_info                          # template information about the words stemmed and without stopwords and occurences

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
        obj['template_info'] = self.template_info.to_dict()
        return obj

    def __repr__(self):
        return 'date: {}'.format(self.timestamp)

    def __lt__(self, other):
        return datetime.datetime.fromisoformat(self.timestamp.replace('Z', '+00:00')) < datetime.datetime.fromisoformat(other.timestamp.replace('Z', '+00:00'))


class Page:
    """Class which represent a page containing a list of revisions"""
    def __init__(self, id: str, namespace: str, title: str, revisions: Iterator[Revision], tfidf: Mapping):
        self.id = id                            # page id
        self.namespace = namespace              # page namespace
        self.title = title                      # page title
        self.revisions = revisions              # list of revisions
        self.tfidf=tfidf                        # tf-idf metrics

    def to_dict(self) -> Mapping:
        """Converts the object instance into a dictionary"""
        obj = dict()
        obj['id'] = self.id
        obj['namespace'] = self.namespace
        obj['title'] = self.title
        obj['revisions'] = list()
        for rev in self.revisions:
            obj['revisions'].append(rev.to_dict())
        obj['tf-idf'] = self.tfidf 
        return obj

def extract_revisions(
        mw_page: mwxml.Page,
        stats: Mapping,
        only_last_revision: bool,
        language: str) -> Iterator[Revision]:
    
    """Extracts the history of a user_warning_template within a template page -> most important keywords."""
    revisions = more_itertools.peekable(mw_page)

    # Newest revisions, useful only if the only_last_revision flag is set equal to true
    newest_revision = None

    for mw_revision in revisions:
        utils.dot()

        # check if it's last revision
        is_last_revision = not utils.has_next(revisions)

        # remove html comments
        text = utils.remove_comments(mw_revision.text or '')

        # extract the template text and other info
        template_info = extractors.user_warnings_template_words.userwarnings_words_extractor(text, language)

        # Build the revision
        rev = Revision(
            id=mw_revision.id,
            user=mw_revision.user,
            text=text,
            timestamp=mw_revision.timestamp.to_json(),
            template_info=template_info,
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

        # Update stats
        stats['performance']['revisions_analyzed'] += 1

        # requested only the last revision
        if only_last_revision:
            if is_last_revision:
                yield newest_revision
        else:
            yield rev

def extract_pages(
        dump: Iterable[mwxml.Page],
        stats: Mapping,
        only_last_revision: bool,
        set_interval: Optional[str],
        esclude_template_repetition: bool,
        language: str) -> Iterator[Page]:
    """Extract the templates from an user page."""

    # Loop on all the pages in the dump, one at a time
    for mw_page in dump:
        utils.log("Processing", mw_page.title)
        
        # Skip non-template, according to https://en.wikipedia.org/wiki/Wikipedia:Namespace
        if mw_page.namespace != 10 or not mw_page.title.lower() in user_warnings_templates:
            utils.log('Skipped (namespace != 10 or different template from the user warnings ones)')
            continue

        revisions_generator = extract_revisions(
            mw_page,
            stats=stats,
            only_last_revision=only_last_revision,
            language=language
        )

        revisions_list = list(revisions_generator)

        revisions_list.sort()
        filtered_revisions_list = list()

        # reference revisions
        reference_rev  = None
        # take the first reference revision and insert it
        if revisions_list:
            reference_rev = revisions_list[0]
            filtered_revisions_list.append(reference_rev)

        # partition time by time interval specified by set_interval
        if set_interval or esclude_template_repetition:
            for elem in revisions_list:
                # ge the last inserted and current time interval
                last_inserted_time =  datetime.datetime.fromisoformat(reference_rev.timestamp.replace('Z', '+00:00'))
                current_time = datetime.datetime.fromisoformat(elem.timestamp.replace('Z', '+00:00'))
                condition = True
                if set_interval:
                    # condition for the time interval
                    condition = condition and (current_time - last_inserted_time).total_seconds() < time_interval_in_seconds[set_interval]
                if esclude_template_repetition:
                    # condition for the different regexp
                    condition = condition and reference_rev.template_info.template_text != elem.template_info.template_text
                if condition:
                    filtered_revisions_list[-1] = elem      # substitute because included in the time interval (partitioned by the time interval)
                else:
                    # if there is the different regexp selected then inserted only if the previous one has different regexp than the current one
                    if not (esclude_template_repetition and reference_rev.template_info.template_text == elem.template_info.template_text):
                        filtered_revisions_list.append(elem)
                        reference_rev = elem
        else:
            # no tag selected
            filtered_revisions_list = revisions_list

        # element occur in document
        is_in_document_dict = dict()
        corpus_size = len(filtered_revisions_list)
        for revision in filtered_revisions_list:
            for word in revision.template_info.inf_retrieval:
                if not word in is_in_document_dict:
                    is_in_document_dict[word] = 1
                else:
                    is_in_document_dict[word] += 1

        idf_dict = dict()   # idf per corpus
        for word in is_in_document_dict:
            idf_dict[word] = math.log(corpus_size / is_in_document_dict[word], 10)
            
        tfidf = dict() # the corpus is constant, so it will be indicized by word and document
        for word in is_in_document_dict: # for every word
            tfidf[word] = dict()
            for doc_index in range(len(filtered_revisions_list)): # for all document
                rev = filtered_revisions_list[doc_index]
                if word in rev.template_info.inf_retrieval:
                    tf = rev.template_info.inf_retrieval[word] / rev.template_info.total_number_words
                else:
                    tf = 0
                tfidf[word][doc_index] = tf * idf_dict[word]
       
        stats['user_warnings_templates'][mw_page.title] = tfidf

        page = Page(
            id=mw_page.id,
            namespace=mw_page.namespace,
            title=mw_page.title,
            revisions=filtered_revisions_list,
            tfidf=tfidf
        )

        yield page

        break

def configure_subparsers(subparsers):
    """Configure a new subparser for the known languages."""
    parser = subparsers.add_parser(
        'extract-user-warnings-templates-tokens',
        help='Extract the tokens of the templates of the users warnings',
    )
    parser.add_argument(
        '--only-last-revision',
        action='store_true',
        help='Consider only the last revision for each page.',
    )
    parser.add_argument(
        '--set-interval',
        choices={None, '1 day', '1 week'},
        required=False,
        default=None,
        help='Time interval at the end of which to return the revison',
    )
    parser.add_argument(
        '--esclude-template-repetition',
        action='store_true',
        help='It does not return a revision if the same template was previously declared',
    )
    parser.add_argument(
        '--language',
        choices={'italian', 'catalan', 'spanish', 'english'},
        required=True,
        help='Language of the analyzed dump',
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
        'user_warnings_templates': dict() # maybe the top 5 or all the best templates
    }

    pages_generator = extract_pages(
        dump,
        stats=stats,
        only_last_revision=args.only_last_revision,
        set_interval=args.set_interval,
        esclude_template_repetition=args.esclude_template_repetition,
        language=args.language
    )

    stats['performance']['start_time'] = datetime.datetime.utcnow()

    for obj in pages_generator:
        features_output_h.write(json.dumps(obj.to_dict(), indent=4))
        features_output_h.write("\n")
    
    stats['performance']['end_time'] = datetime.datetime.utcnow()
    stats_output_h.write(json.dumps(stats, indent=4, default=str))