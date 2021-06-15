import os
import sys
import gzip
import json
import datetime

stats_output_obj = dict()

if __name__ == "__main__":

    folder = sys.argv[1]            # dumps folders
    output_folder = sys.argv[2]     # output folder
    param_name = sys.argv[3]        # iwiki, enwiki ...
    param_date = sys.argv[4]        # 20210201
    counter = 0                     # file counter
    stats_counter = 0               # stats file counter

    if len(sys.argv) < 5:
        print('No arguments provided')
        exit(1)

    feature_file = gzip.open('{}/{}_{}_language_dataset.json.gz'.format(output_folder, param_name, param_date), 'wb')
    stats_file = gzip.open('{}/{}_{}_language_stats.json.gz'.format(output_folder, param_name, param_date), 'wb')

    for filename in os.listdir(folder):

        try:
            name, date, other = filename.split("-", 2)
        except:
            continue

        if name == param_name and date == param_date and filename.endswith('.features.json.gz'):
            
            # merge the file line
            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                for line in f:
                    feature_file.write(line)
            counter += 1
        
        elif name == param_name and date == param_date and filename.endswith('.stats.json.gz'):
            stats_obj = None
            
            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                stats_obj = json.loads(f.read().decode('utf-8'))
            stats_counter += 1

            # merge the statistic files

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

            if not 'users' in stats_output_obj:
                stats_output_obj['users'] = dict()
            
            if not 'total' in stats_output_obj['users']:
                if 'total' in stats_obj['users']:
                    stats_output_obj['users']['total'] = int(stats_obj['users']['total'])
            else:
                stats_output_obj['users']['total'] += int(stats_obj['users']['total'])

            if not 'languages' in stats_output_obj['users']:
                stats_output_obj['users']['languages'] = dict()
            
            for lang in stats_obj['users']['languages']:
                if not lang in stats_output_obj['users']['languages']:
                    stats_output_obj['users']['languages'][lang] = dict()
                    stats_output_obj['users']['languages'][lang]['knowledge'] = [0, 0, 0, 0, 0, 0, 0]
                for index, value in enumerate(stats_obj['users']['languages'][lang]['knowledge']):
                    stats_output_obj['users']['languages'][lang]['knowledge'][index] += value
        else:
            continue

    print('Found: {} files and {} stats'.format(counter, stats_counter))

    if counter != 0:
        stats_output_obj['users']['num_unique_languages'] = len(stats_output_obj['users']['languages'])
        stats_output_obj['performance']['start_time'] = str(stats_output_obj['performance']['start_time'])
        stats_output_obj['performance']['end_time'] = str(stats_output_obj['performance']['end_time'])

    stats_file.write(json.dumps(stats_output_obj, indent=4).encode('utf-8'))

    feature_file.close()
    stats_file.close()