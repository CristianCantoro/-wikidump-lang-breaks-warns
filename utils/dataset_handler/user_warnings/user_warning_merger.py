import os
import sys
import gzip
import json
import datetime

stats_output_obj = dict()

if __name__ == "__main__":

    folder_1 = sys.argv[1]
    folder_2 = sys.argv[2]
    output_folder = sys.argv[3]
    param_name = sys.argv[4]
    param_date = sys.argv[5]
    language = sys.argv[6]
    counter = 0
    stats_counter = 0

    if len(sys.argv) < 7:
        print('No arguments provided')
        exit(1)

    feature_file = gzip.open('{}/{}_{}_user_warnigs_merged_dataset.json.gz'.format(output_folder, param_name, param_date), 'wb')
    stats_file = gzip.open('{}/{}_{}_user_warnigs_merged_stats.json.gz'.format(output_folder, param_name, param_date), 'wb')

    file_list = [ '/'.join([folder_1, filename]) for filename in os.listdir(folder_1) ] + [ '/'.join([folder_2, filename]) for filename in os.listdir(folder_2) ]

    for filename in file_list:

        print(filename)

        try:
            name, date, other = os.path.basename(filename).split("_", 2)
        except:
            print('Discarded:', filename)
            continue

        if name == param_name and date == param_date and filename.endswith('dataset.json.gz'):
            with gzip.open(filename, 'rb') as f:
                for line in f:
                    feature_file.write(line)
            counter += 1
        elif name == param_name and date == param_date and filename.endswith('stats.json.gz'):
            stats_obj = None

            with gzip.open(filename, 'rb') as f:
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

            if not 'user_warnings' in stats_output_obj:
                stats_output_obj['user_warnings'] = dict()
                stats_output_obj['user_warnings']['total_user_talk_pages_transcluded'] = 0
                stats_output_obj['user_warnings']['users_transcluded'] = 0
                stats_output_obj['user_warnings']['users_at_least_parameter_transcluded'] = 0
                stats_output_obj['user_warnings']['total_user_talk_pages_substituted'] = 0
                stats_output_obj['user_warnings']['user_template_occurences'] = dict()
                stats_output_obj['categories'] = dict()

            if 'user_warnings' in stats_obj:
                # the warnings for transcluded one
                stats_output_obj['user_warnings']['total_user_talk_pages_transcluded'] += stats_obj['user_warnings']['total_user_talk_pages']
                stats_output_obj['user_warnings']['users_transcluded'] += stats_obj['user_warnings']['users']
                stats_output_obj['user_warnings']['users_at_least_parameter_transcluded'] += stats_obj['user_warnings']['users_at_least_parameter']
                for lang in stats_obj['user_warnings']['user_template_occurences']:
                    if not lang in stats_output_obj['user_warnings']['user_template_occurences']:
                        stats_output_obj['user_warnings']['user_template_occurences'][lang] = dict()
                    for u_w in stats_obj['user_warnings']['user_template_occurences'][lang]:
                        if not u_w in stats_output_obj['user_warnings']['user_template_occurences'][lang]:
                            stats_output_obj['user_warnings']['user_template_occurences'][lang][u_w] = dict()
                            stats_output_obj['user_warnings']['user_template_occurences'][lang][u_w]['user_talk_occurences_transcluded'] = 0
                            stats_output_obj['user_warnings']['user_template_occurences'][lang][u_w]['user_talk_occurences_with_params_transcluded'] = 0
                            stats_output_obj['user_warnings']['user_template_occurences'][lang][u_w]['user_talk_occurences_substituted'] = 0
                        stats_output_obj['user_warnings']['user_template_occurences'][lang][u_w]['user_talk_occurences_transcluded'] += stats_obj['user_warnings']['user_template_occurences'][lang][u_w]['user_talk_occurences']
                        stats_output_obj['user_warnings']['user_template_occurences'][lang][u_w]['user_talk_occurences_with_params_transcluded'] += stats_obj['user_warnings']['user_template_occurences'][lang][u_w]['user_talk_occurences_with_params']

                for lang in stats_obj['user_warnings']['categories']:
                    if not lang in stats_output_obj['categories']:
                        stats_output_obj['categories'][lang] = dict()
                    for category in stats_obj['user_warnings']['categories'][lang]:
                        if not category in stats_output_obj['categories'][lang]:
                            stats_output_obj['categories'][lang][category] = dict()
                            stats_output_obj['categories'][lang][category]['users_transcluded'] = 0
                            stats_output_obj['categories'][lang][category]['users_substituted'] = 0
                            stats_output_obj['categories'][lang][category]['total_transcluded'] = 0
                        stats_output_obj['categories'][lang][category]['users_transcluded'] += stats_obj['user_warnings']['categories'][lang][category]['users']
                        stats_output_obj['categories'][lang][category]['users_substituted'] += stats_obj['user_warnings']['categories'][lang][category]['total']

            else:
                
                # unficare visto che la lingua la so, non era necessario metterla
                stats_output_obj['user_warnings']['total_user_talk_pages_substituted'] += stats_obj['user_warnings_stats']['total']

                for u_w in stats_obj['user_warnings_stats']['template_recognized']:
                    if not language in stats_output_obj['user_warnings']['user_template_occurences']:
                        stats_output_obj['user_warnings']['user_template_occurences'][language] = dict()
                    if not u_w in stats_output_obj['user_warnings']['user_template_occurences'][language]:
                        stats_output_obj['user_warnings']['user_template_occurences'][language][u_w] = dict()
                        stats_output_obj['user_warnings']['user_template_occurences'][language][u_w]['user_talk_occurences_transcluded'] = 0
                        stats_output_obj['user_warnings']['user_template_occurences'][language][u_w]['user_talk_occurences_with_params_transcluded'] = 0
                        stats_output_obj['user_warnings']['user_template_occurences'][language][u_w]['user_talk_occurences_substituted'] = 0
                    stats_output_obj['user_warnings']['user_template_occurences'][language][u_w]['user_talk_occurences_substituted'] += stats_obj['user_warnings_stats']['template_recognized'][u_w]['occurences']
                    if not language in stats_output_obj['categories']:
                        stats_output_obj['categories'][language] = dict()
                    category = stats_obj['user_warnings_stats']['template_recognized'][u_w]['category']
                    if not category in stats_output_obj['categories'][language]:
                        stats_output_obj['categories'][language][category] = dict()
                        stats_output_obj['categories'][language][category]['users_transcluded'] = 0
                        stats_output_obj['categories'][language][category]['users_substituted'] = 0
                        stats_output_obj['categories'][language][category]['total_transcluded'] = 0
                    stats_output_obj['categories'][language][category]['users_substituted'] += stats_obj['user_warnings_stats']['template_recognized'][u_w]['occurences']

    print('Found: {} files and {} stats'.format(counter, stats_counter))

    stats_output_obj['performance']['start_time'] = str(stats_output_obj['performance']['start_time'])
    stats_output_obj['performance']['end_time'] = str(stats_output_obj['performance']['end_time'])

    stats_file.write(json.dumps(stats_output_obj, indent=4).encode('utf-8'))

    feature_file.close()
    stats_file.close()