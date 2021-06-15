import os
import sys
import gzip
import json
import datetime

def analyze_line(line: str, feature_file: str) -> None:
    """
    Retrives the languages from the revision associated to the user and saves it

    Args:
        line (str): current line
        feature_file (str): feature file name
    """
    language_line = json.loads(line.decode('utf-8'))
    new_language = dict()
    new_language['name'] = language_line['title']
    new_language['id'] = language_line['id']
    new_language['num_languages_declared'] = language_line['revisions'][0]['num_languages_declared']
    new_language['edit_date'] = language_line['revisions'][0]['timestamp']
    new_language['languages'] = language_line['revisions'][0]['languages']
    # save the refactored language
    feature_file.write(json.dumps(new_language).encode('utf-8'))
    feature_file.write('\n'.encode('utf-8'))

if __name__ == "__main__":

    folder = sys.argv[1]            # dump folder
    output_folder = sys.argv[2]     # output folder
    param_name = sys.argv[3]        # param name
    param_date = sys.argv[4]        # param date

    if len(sys.argv) < 5:
        print('No arguments provided')
        exit(1)

    feature_file = gzip.open('{}/{}_{}_refactored_language_dataset.json.gz'.format(output_folder, param_name, param_date), 'wb')
    stats_file = gzip.open('{}/{}_{}_refactored_language_stats.json.gz'.format(output_folder, param_name, param_date), 'wb')

    for filename in os.listdir(folder):

        try:
            name, date, other = filename.split("_", 2)
        except:
            continue

        if name == param_name and date == param_date and filename.endswith('dataset.json.gz'):
            # the language files have been refactored
            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                for line in f:
                    analyze_line(line, feature_file)

        elif name == param_name and date == param_date and filename.endswith('stats.json.gz'):
            stats_obj = None
            # the statistics file remains the same
            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                for line in f:
                    stats_file.write(line)
        else:
            continue

    feature_file.close()
    stats_file.close()