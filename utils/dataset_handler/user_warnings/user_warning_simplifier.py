import os
import sys
import gzip
import json
import datetime
from io import TextIOWrapper
from typing import Tuple
from backports.datetime_fromisoformat import MonkeyPatch
from collections import OrderedDict

# Polyfiller for retrocompatibiliy with Python3.5
MonkeyPatch.patch_fromisoformat()

class Parameters:
    """
    Parameters class
    """
    def __init__(self, timestamp: datetime.datetime, options: dict):
        self.timestamp = timestamp
        self.options = options

    def to_dict(self) -> dict:
        obj = dict()
        obj['timestamp'] = self.timestamp
        obj['options'] = self.options
        return obj

class UserWarning:
    """
    User Warnings class
    """
    def __init__(self, user_warning_name: str, transcluded: bool, parameters: list(), category: str):
        self.user_warning_name = user_warning_name
        self.transcluded = transcluded
        self.parameters = parameters
        self.category = category

    def to_dict(self) -> dict:
        obj = dict()
        obj['user_warning_name'] = self.user_warning_name
        obj['transcluded'] = self.transcluded
        obj['parameters'] = list()
        for val in self.parameters:
            obj['parameters'].append(val.to_dict())
        obj['category'] = self.category
        return obj

class User:
    """
    User class
    """
    def __init__(self, name: str):
        self.name = name
        self.id_talk_page = None
        self.user_warnings_stats = OrderedDict()
        self.user_warnings_received = list()

    def to_dict(self) -> dict:
        obj = dict()
        obj['name'] = self.name
        obj['id_talk_page'] = self.id_talk_page
        obj['user_warnings_stats'] = self.user_warnings_stats
        obj['user_warnings_received'] = list()
        for uw in self.user_warnings_received:
            obj['user_warnings_received'].append(uw.to_dict())
        return obj

def update_user(data: dict, utente: User) -> User:
    """
    Update user

    Args:
        data (dict): new user data
        utente (User): user

    Returns:
        User: updated user
    """

    # salvo le user warning stats
    for year in data['user_warnings_stats']:
        for month in data['user_warnings_stats'][year]:
            for value in data['user_warnings_stats'][year][month]:
                if not year in utente.user_warnings_stats:
                    utente.user_warnings_stats[year] = OrderedDict()
                    utente.user_warnings_stats[year][month] = OrderedDict()
                    utente.user_warnings_stats[year][month][value] = data['user_warnings_stats'][year][month][value]
                elif not month in utente.user_warnings_stats[year]:
                    utente.user_warnings_stats[year][month] = OrderedDict()
                    utente.user_warnings_stats[year][month][value] = data['user_warnings_stats'][year][month][value]
                else:
                    if not value in utente.user_warnings_stats[year][month]:
                        utente.user_warnings_stats[year][month][value] = 0
                    utente.user_warnings_stats[year][month][value] += data['user_warnings_stats'][year][month][value]
    
    # salvo gli user warnings received
    for uw in data['user_warnings_received']:
        parameters = list()
        for param in uw['parameters']:
            parameters.append(Parameters(param['timestamp'], param['options']))
        el = UserWarning(uw['user_warning_name'], uw['transluded'], parameters, uw['category'])
        utente.user_warnings_received.append(el)
    return utente

def store_batch(data: dict, set_analyzed: set, values: dict) -> dict:
    """
    Store new user in the batch

    Args:
        data (dict): new user data
        set_analyzed (set): set of the analyzed users
        values (dict): users' batch

    Returns:
        values dict: new users' batch
    """
    # già analizzato
    if data['name'] in set_analyzed:
        return values
    # da salvare
    if not data['name'] in values:
        # creating the user
        utente = User(data['name'])
        utente.id_talk_page = data['id_talk_page']
        
        # salvo le user warning stats
        for year in data['user_warnings_stats']:
            utente.user_warnings_stats[year] = OrderedDict()
            for month in data['user_warnings_stats'][year]:
                utente.user_warnings_stats[year][month] = OrderedDict()
                for value in data['user_warnings_stats'][year][month]:
                    utente.user_warnings_stats[year][month][value] = data['user_warnings_stats'][year][month][value]
        
        # salvo gli user warnings received
        for uw in data['user_warnings_received']:
            parameters = list()
            for param in uw['parameters']:
                parameters.append(Parameters(param['timestamp'], param['options']))
            el = UserWarning(uw['user_warning_name'], uw['transluded'], parameters, uw['category'])
            utente.user_warnings_received.append(el)

        values[data['name']] = utente
    return values

def save_batch(
    start_line: int, 
    n_written: int, 
    values: dict, 
    feature_file: TextIOWrapper, 
    set_analyzed: set) -> Tuple[bool, int, dict, set, int]:
    """
    Saves the elements within the batch in the feature file

    Args:
        start_line (int): line from which the analysis strats
        n_written (int): number of users written in total
        values (dict): batch of users to write in the feature file
        feature_file (TextIOWrapper): feature file
        set_analyzed (set): set of analyzed users

    Returns:
        Tuple[bool, int, dict, set, int]: 
        - break_loop: end the analysis
        - start_line: new start line
        - values: empty batch
        - set_analyzed: users analyzed
        - n_written: number of lines written
    """
    break_loop = False

    for val in values:
        if not values[val].user_warnings_received:
            print('Something went wrong:', val, 'not found')
            exit(1)
        # write the values in the feature file
        feature_file.write(json.dumps(values[val].to_dict(), default=str).encode('utf-8'))
        feature_file.write('\n'.encode('utf-8'))
        n_written += 1
        set_analyzed.add(val)
    values.clear()
    # whether to stop or not
    if start_line > line_number:
        break_loop = True
    start_line += threshold
    print('Analizzare da {}'.format(start_line))
    return break_loop, start_line, values, set_analyzed, n_written

def analyzed_user_warnings(
    start_line: int, 
    threshold: int, 
    folder: str, 
    filename: str, 
    set_analyzed: set, 
    values: dict,
    n_written: int,
    feature_file: TextIOWrapper) -> Tuple[bool, int, set, dict, int]:
    """
    Method which allows to analyze the user warnings within the file

    Args:
        start_line (int): starting line
        threshold (int): treshold
        folder (str): folder
        filename (str): filename
        set_analyzed (set): set of analyzed users
        values (dict): users' batch
        n_written (int): numver of written user records
        feature_file (TextIOWrapper): feature file

    Returns:
        Tuple[bool, int, set, dict, int]: 
        - break_loop: if the analysis should be stopped, 
        - start_line: line from which the analysis starts, 
        - set_analyzed: set of analyzed users, 
        - values: users in batch, 
        - n_written: number of users written in the feature file
    """

    break_loop = False
    
    with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
        i = 0   # line counter
        for line in f:
            data = json.loads(line.decode('utf-8'))
            if not (i < start_line):
                if i <= start_line + threshold:
                    values = store_batch(
                        data,
                        set_analyzed, 
                        values,
                    )   # store the data in the batch set
                else:
                    # only check if the element is present, then update that user
                    if data['name'] in values:
                        values[data['name']] = update_user(data, values[data['name']])           # user already found: updated
            i += 1
        # save the batch within the feature file
        break_loop, start_line, values, set_analyzed, n_written = save_batch(
            start_line, 
            n_written, 
            values, 
            feature_file, 
            set_analyzed
        )  # save the batch
    return break_loop, start_line, set_analyzed, values, n_written

if __name__ == "__main__":

    folder = sys.argv[1]            # folder
    output_folder = sys.argv[2]     # output folder
    param_name = sys.argv[3]        # parameter name
    param_date = sys.argv[4]        # parameter date

    threshold = 100000              # number of user warnings to keep in memory
    set_analyzed = set()            # user warnings name already analyzed
    n_written = 0                   # warnings written
    values = dict()                 # values

    if len(sys.argv) < 5:
        print('No arguments provided')
        exit(1)

    # files
    feature_file = gzip.open('{}/{}_{}_user_warnigs_dataset.json.gz'.format(output_folder, param_name, param_date), 'wb')
    stats_file = gzip.open('{}/{}_{}_user_warnigs_stats.json.gz'.format(output_folder, param_name, param_date), 'wb')

    for filename in os.listdir(folder):

        try:
            name, date, other = filename.split("_", 2)
        except:
            print('Discarded:', filename)
            continue

        if name == param_name and date == param_date and filename.endswith('dataset.json.gz'):
            line_number = 0

            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                line_number = sum(1 for _ in f)

            start_line = 0  # starting line

            break_loop = False

            # until break_loop is true
            while not break_loop:
                # analyze the warnings in a loop
                break_loop, start_line, set_analyzed, values, n_written = analyzed_user_warnings(
                    start_line, 
                    threshold, 
                    folder, 
                    filename, 
                    set_analyzed, 
                    values,
                    n_written,
                    feature_file
                )

        elif name == param_name and date == param_date and filename.endswith('stats.json.gz'):
            # statistics remain the same as before
            stats_obj = None
            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                for line in f:
                    stats_file.write(line)
        else:
            continue

    print(len(set_analyzed), n_written)

    feature_file.close()
    stats_file.close()