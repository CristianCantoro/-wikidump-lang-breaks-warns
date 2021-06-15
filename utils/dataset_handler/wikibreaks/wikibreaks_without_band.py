import os
import sys
import gzip
import json

stats_output_obj = dict()

if __name__ == "__main__":
    """
    This script removes the band template, which is a way to declare a user is busy in the Uzbek language, but has other meaning in the current Wikipedia language
    """

    folder = sys.argv[1]
    output_folder = sys.argv[2]
    param_name = sys.argv[3]
    param_date = sys.argv[4]
    counter = 0
    stats_counter = 0

    if len(sys.argv) < 5:
        print('No arguments provided')
        exit(1)

    feature_file = gzip.open('{}/{}_{}_wikibreaks_without_band_refactored.json.gz'.format(output_folder, param_name, param_date), 'wb')

    for filename in os.listdir(folder):

        filename = '{}/{}'.format(folder, filename)
        print(filename)

        try:
            name, date, other = os.path.basename(filename).split("_", 2)
        except:
            print('flex', filename)
            continue

        if name == param_name and date == param_date and filename.endswith('dataset.json.gz'):
            print('opened {}'.format(filename))
            with gzip.open(filename, 'rb') as f:
                for line in f:
                    data = json.loads(line.decode('utf-8'))
                    new_wb_list = list()
                    # remove the band template from the wikibreaks
                    for wb in data['wikibreaks']:
                        if wb['name'] != 'band':
                            new_wb_list.append(wb)
                    if new_wb_list:
                        data['wikibreaks'] = new_wb_list
                        feature_file.write(json.dumps(data, default=str).encode('utf-8'))
                        feature_file.write('\n'.encode('utf-8'))
            counter += 1
        elif name == param_name and date == param_date and filename.endswith('stats.json.gz'):
            continue
    print('Found: {} files and {} stats'.format(counter, stats_counter))

    feature_file.close()