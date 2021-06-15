import os
import sys
import gzip
import json
import datetime
from collections import OrderedDict
from backports.datetime_fromisoformat import MonkeyPatch

# Polyfiller for retrocompatibiliy with Python3.5
MonkeyPatch.patch_fromisoformat()

class Parameter:
    def __init__(self, timestamp: str, options: dict):
        self.timestamp = timestamp
        self.options = options
    
    def to_dict(self):
        obj = dict()
        obj['timestamp'] = self.timestamp
        obj['options'] = self.options
        return obj

    def __eq__(self, other):
        return self.options == other.options


class UserWarning:
    def __init__(self, uw_name: str, options: list, category: str, transluded: bool):
        self.user_warning_name = uw_name
        self.options = options
        self.category = category
        self.transluded = transluded

    def to_dict(self):
        obj = dict()
        obj['user_warning_name'] = self.user_warning_name
        obj['parameters'] = list()
        obj['category'] = self.category
        obj['transluded'] = self.transluded
        for param in self.options:
            obj['parameters'].append(param.to_dict())
        return obj

    def __eq__(self, other):
        if self.options and other.options:
            return self.user_warning_name == other.user_warning_name and self.options[-1] == other.options[-1]
        else:
            return self.user_warning_name == other.user_warning_name

def analyze_revision(first_rev: bool, uw_per_year: dict, uw_found: dict):
    if first_rev:
        date_init = datetime.datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))
        date_now = datetime.datetime.utcnow()
        for year in range(date_init.year, date_now.year + 1):
            uw_per_year[year] = OrderedDict()
            for month in range(1, 13):
                uw_per_year[year][month] = dict()
                uw_per_year[year][month]['not_serious_transcluded'] = 0
                uw_per_year[year][month]['warning_transcluded'] = 0
                uw_per_year[year][month]['serious_transcluded'] = 0
                uw_per_year[year][month]['not_serious_substituted'] = 0
                uw_per_year[year][month]['warning_substituted'] = 0
                uw_per_year[year][month]['serious_substituted'] = 0
    
    first_rev = False

    template_occurences_index = dict()

    for u_w in rev['templates']:
        if not u_w['name'] in uw_found:
            param = Parameter(rev['timestamp'], dict())
            uw_found[u_w['name']] = [ UserWarning(u_w['name'], [param], u_w['category'], False) ]
            date_uw = datetime.datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))
            uw_per_year[date_uw.year][date_uw.month][u_w['category'] + '_substituted'] += 1
            template_occurences_index[u_w['name']] = 0
        else:
            if not u_w['name'] in template_occurences_index:
                template_occurences_index[u_w['name']] = 0
            else:
                template_occurences_index[u_w['name']] += 1

            # same but newone
            if template_occurences_index[u_w['name']] >= len(uw_found[u_w['name']][template_occurences_index[u_w['name']]].options):
                param = Parameter(rev['timestamp'], u_w['options'])
                uw_found[u_w['name']].append(UserWarning(u_w['name'], [param], u_w['category'], False))
                date_uw = datetime.datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))
                uw_per_year[date_uw.year][date_uw.month][u_w['category'] + '_substituted'] += 1
            else:
                param = Parameter(rev['timestamp'], u_w['options'])
                if uw_found[u_w['name']][template_occurences_index[u_w['name']]].options[-1] != param:
                    uw_found[u_w['name']][template_occurences_index[u_w['name']]].options.append(param)

    return uw_per_year, uw_found

if __name__ == "__main__":

    folder = sys.argv[1]
    output_folder = sys.argv[2]
    param_name = sys.argv[3]
    param_date = sys.argv[4]

    counter = 0
    stats_counter = 0

    if len(sys.argv) < 5:
        print('No arguments provided')
        exit(1)

    feature_file = gzip.open('{}/{}_{}_refactored_user_warnigs_substituted_dataset.json.gz'.format(output_folder, param_name, param_date), 'wb')
    stats_file = gzip.open('{}/{}_{}_refactored_user_warnigs_substituted_stats.json.gz'.format(output_folder, param_name, param_date), 'wb')

    for filename in os.listdir(folder):

        try:
            name, date, other = filename.split("_", 2)
        except:
            continue

        if name == param_name and date == param_date and filename.endswith('dataset.json.gz'):
            print('File aperto')
            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                for line in f:
                    user_warning = json.loads(line.decode('utf-8'))
                    new_user_warning_transcluded = dict()
                    new_user_warning_transcluded['name'] = user_warning['title']
                    new_user_warning_transcluded['id_talk_page'] = user_warning['id']
                    uw_found = dict()
                    uw_per_year = OrderedDict()
                    
                    first_rev = True
                    
                    for rev in user_warning['revisions']:
                        uw_per_year, uw_found = analyze_revision(first_rev, uw_per_year, uw_found)

                    new_user_warning_transcluded['user_warnings_stats'] = uw_per_year
                    new_user_warning_transcluded['user_warnings_received'] = list()
                    for u_w in uw_found:
                        for duplicate in uw_found[u_w]:
                            new_user_warning_transcluded['user_warnings_received'].append(duplicate.to_dict())
                    feature_file.write(json.dumps(new_user_warning_transcluded).encode('utf-8'))
                    feature_file.write('\n'.encode('utf-8'))
            counter += 1
        elif name == param_name and date == param_date and filename.endswith('stats.json.gz'):
            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                for line in f:
                    stats_file.write(line)
            stats_counter += 1
        else:
            continue

    print('Found: {} features files and {} stats'.format(counter, stats_counter))

    feature_file.close()
    stats_file.close()