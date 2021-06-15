import os
import sys
import gzip
import json
import datetime

# dictionary stats
stats_output_obj = dict()

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

    # feature and stats file
    feature_file = gzip.open('{}/{}_{}_wikibreaks_dataset.json.gz'.format(output_folder, param_name, param_date), 'wb')
    stats_file = gzip.open('{}/{}_{}_wikibreaks_stats.json.gz'.format(output_folder, param_name, param_date), 'wb')

    for filename in os.listdir(folder):

        try:
            name, date, other = filename.split("-", 2)
        except:
            print('Discarded:', filename)
            continue

        if name == param_name and date == param_date and filename.endswith('.features.json.gz'):
            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                # write the line in the merged file
                for line in f:
                    feature_file.write(line)
            counter += 1
        elif name == param_name and date == param_date and filename.endswith('.stats.json.gz'):
            stats_obj = None

            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                stats_obj = json.loads(f.read().decode('utf-8'))
            stats_counter += 1

            # merge the statistics in a merged file

            if not 'performance' in stats_output_obj:
                stats_output_obj['performance'] = dict()
            
            if not 'start_time' in stats_output_obj['performance']:
                if 'start_time' in stats_obj['performance']:
                    stats_output_obj['performance']['start_time'] = datetime.datetime.strptime(stats_obj['performance']['start_time'], '%Y-%m-%d %H:%M:%S.%f')
            else:
                tmp = datetime.datetime.strptime(stats_obj['performance']['start_time'], '%Y-%m-%d %H:%M:%S.%f')
                if stats_output_obj['performance']['start_time'] > tmp:
                    stats_output_obj['performance']['start_time'] = tmp

            if not 'end_time' in stats_output_obj['performance']:
                if 'end_time' in stats_obj['performance']:
                    stats_output_obj['performance']['end_time'] = datetime.datetime.strptime(stats_obj['performance']['end_time'], '%Y-%m-%d %H:%M:%S.%f')
            else:
                tmp = datetime.datetime.strptime(stats_obj['performance']['end_time'], '%Y-%m-%d %H:%M:%S.%f')
                if stats_output_obj['performance']['end_time'] < tmp:
                    stats_output_obj['performance']['end_time'] = tmp

            if not 'pages_analyzed' in stats_output_obj['performance']:
                if 'pages_analyzed' in stats_obj['performance']:
                    stats_output_obj['performance']['pages_analyzed'] = int(stats_obj['performance']['pages_analyzed'])
            else:
                stats_output_obj['performance']['pages_analyzed'] += int(stats_obj['performance']['pages_analyzed'])

            if not 'revisions_analyzed' in stats_output_obj['performance']:
                if 'revisions_analyzed' in stats_obj['performance']:
                    stats_output_obj['performance']['revisions_analyzed'] = int(stats_obj['performance']['revisions_analyzed'])
            else:
                stats_output_obj['performance']['revisions_analyzed'] += int(stats_obj['performance']['revisions_analyzed'])

            if not 'wikibreaks' in  stats_output_obj:
                stats_output_obj['wikibreaks'] = dict()
                stats_output_obj['wikibreaks']['users'] = 0
                stats_output_obj['wikibreaks']['user_subcategories_occurences'] = dict()
                stats_output_obj['wikibreaks']['users_at_least_parameter'] = 0
                stats_output_obj['wikibreaks']['user_categories_occurences'] = dict()
                stats_output_obj['wikibreaks']['templates_at_least_one_parameter'] = 0
                stats_output_obj['wikibreaks']['templates'] = 0

            stats_output_obj['wikibreaks']['users'] += stats_obj['wikibreaks']['users']
            stats_output_obj['wikibreaks']['users_at_least_parameter'] += stats_obj['wikibreaks']['users_at_least_parameter']
            stats_output_obj['wikibreaks']['templates_at_least_one_parameter'] += stats_obj['wikibreaks']['templates_at_least_one_parameter']
            stats_output_obj['wikibreaks']['templates'] += stats_obj['wikibreaks']['templates']

            for w_b in stats_obj['wikibreaks']['user_subcategories_occurences']:
                if not w_b in stats_output_obj['wikibreaks']['user_subcategories_occurences']:
                    stats_output_obj['wikibreaks']['user_subcategories_occurences'][w_b] = dict()
                    stats_output_obj['wikibreaks']['user_subcategories_occurences'][w_b]['total'] = 0
                    stats_output_obj['wikibreaks']['user_subcategories_occurences'][w_b]['with_params'] = 0

                for stats in stats_obj['wikibreaks']['user_subcategories_occurences'][w_b]:
                    stats_output_obj['wikibreaks']['user_subcategories_occurences'][w_b][stats] += stats_obj['wikibreaks']['user_subcategories_occurences'][w_b][stats]
            
            for w_b in stats_obj['wikibreaks']['user_categories_occurences']:
                if not w_b in stats_output_obj['wikibreaks']['user_categories_occurences']:
                    stats_output_obj['wikibreaks']['user_categories_occurences'][w_b] = dict()
                    stats_output_obj['wikibreaks']['user_categories_occurences'][w_b]['total'] = 0
                    stats_output_obj['wikibreaks']['user_categories_occurences'][w_b]['with_params'] = 0

                for stats in stats_obj['wikibreaks']['user_categories_occurences'][w_b]:
                    stats_output_obj['wikibreaks']['user_categories_occurences'][w_b][stats] += stats_obj['wikibreaks']['user_categories_occurences'][w_b][stats]
        else:
            continue

    print('Found: {} features files and {} stats'.format(counter, stats_counter))

    if counter != 0:
        # if a file is found, then update the start and the end time
        stats_output_obj['performance']['start_time'] = str(stats_output_obj['performance']['start_time'])
        stats_output_obj['performance']['end_time'] = str(stats_output_obj['performance']['end_time'])

    stats_file.write(json.dumps(stats_output_obj, indent=4).encode('utf-8'))

    feature_file.close()
    stats_file.close()