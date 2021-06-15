import os
import sys
import gzip
import json
import datetime

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

    feature_file = gzip.open('{}/{}_{}_user_warnigs_substituted_dataset.json.gz'.format(output_folder, param_name, param_date), 'wb')
    stats_file = gzip.open('{}/{}_{}_user_warnigs_substituted_stats.json.gz'.format(output_folder, param_name, param_date), 'wb')

    for filename in os.listdir(folder):

        try:
            name, date, other = filename.split("-", 2)
        except:
            continue

        if name == param_name and date == param_date and filename.endswith('.features.json.gz'):
            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                for line in f:
                    feature_file.write(line)
            counter += 1
        elif name == param_name and date == param_date and filename.endswith('.stats.json.gz'):
            stats_obj = None

            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                stats_obj = json.loads(f.read().decode('utf-8'))
            stats_counter += 1

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

            if not 'user_warnings_stats' in stats_output_obj:
                stats_output_obj['user_warnings_stats'] = dict()
                stats_output_obj['user_warnings_stats']['total'] = 0
                stats_output_obj['user_warnings_stats']['template_recognized'] = dict()

            stats_output_obj['user_warnings_stats']['total'] += stats_obj['user_warnings_stats']['total']

            for template_name in stats_obj['user_warnings_stats']['template_recognized']:
                if not template_name in stats_output_obj['user_warnings_stats']['template_recognized']:
                    stats_output_obj['user_warnings_stats']['template_recognized'][template_name] = dict()
                    stats_output_obj['user_warnings_stats']['template_recognized'][template_name]['category'] = stats_obj['user_warnings_stats']['template_recognized'][template_name]['category']
                    stats_output_obj['user_warnings_stats']['template_recognized'][template_name]['occurences'] = 0
                stats_output_obj['user_warnings_stats']['template_recognized'][template_name]['occurences'] += stats_obj['user_warnings_stats']['template_recognized'][template_name]['occurences']
        else:
            continue

    print('Found: {} files and {} stats'.format(counter, stats_counter))

    if counter != 0:
        stats_output_obj['performance']['start_time'] = str(stats_output_obj['performance']['start_time'])
        stats_output_obj['performance']['end_time'] = str(stats_output_obj['performance']['end_time'])

    stats_file.write(json.dumps(stats_output_obj, indent=4).encode('utf-8'))

    feature_file.close()
    stats_file.close()