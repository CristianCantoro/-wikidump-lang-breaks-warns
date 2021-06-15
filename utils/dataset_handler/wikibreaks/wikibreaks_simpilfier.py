import os
import sys
import gzip
import json
import datetime
import copy
from io import TextIOWrapper
from typing import Tuple
from backports.datetime_fromisoformat import MonkeyPatch

# Polyfiller for retrocompatibiliy with Python3.5
MonkeyPatch.patch_fromisoformat()

class Parameters:
    """
    Parameters class, it represent the parameters of a wikibreak
    """
    def __init__(self, timestamp: datetime.datetime, options: dict):
        self.timestamp = timestamp
        self.options = options
    
    def __eq__(self, other):
        # equal
        return self.options == other.options

    def to_dict(self) -> dict:
        # object to dictionary
        obj = dict()
        obj['timestamp'] = self.timestamp
        obj['options'] = self.options
        return obj

class Wikibreak:
    """
    Wikibreak class, it represent the wikibreak associated with the user
    """
    def __init__(self, from_date: datetime.datetime, name: str, options: list, categories: list, subcategory: str):
        """
        Init method
        Args:
            from_date (datetime.datetime): starting date
            name (str): name
            options (list): options
            categories (list): categories
            subcategory (str): subcategory
        """
        self.from_date = from_date
        self.to_date = None
        self.options = options
        self.name = name
        self.categories = categories
        self.subcategory = subcategory

    def overlap(self, other) -> bool:
        """
        Check if there is an overlap when the wikibreaks are merged considering user pages and user talk page

        Args:
            other ([Wikibreak]): other wikibreak

        Returns:
            [bool]: whether there is an overlap or not
        """
        if self.name == other.name:
            if other.from_date < self.from_date and (other.to_date == None or other.to_date > self.from_date):
                return True
            elif (self.to_date == None or other.from_date < self.to_date) and self.from_date < other.from_date:
                return True
        return False

    def __eq__(self, other) -> bool:
        return self.options == other.options and self.name == other.name

    def __lt__(self, other) -> bool:
        if self.from_date == other.from_date:
            if not self.to_date:
                return False
            elif not other.to_date:
                return True
            else:
                return self.to_date < other.to_date
        return self.from_date < other.from_date

    def to_dict(self) -> dict:
        obj = dict()
        obj['from_date'] = self.from_date
        obj['to_date'] = self.to_date
        obj['parameters'] = list()
        for val in self.options:
            obj['parameters'].append(val.to_dict())
        obj['name'] = self.name
        obj['categories'] = list()
        obj['subcategory'] = self.subcategory
        for cat in self.categories:
            obj['categories'].append(cat)
        return obj

class User:
    """
    Class which represent an User
    """
    def __init__(self, name: str):
        self.name = name
        self.id_talk_page = None
        self.id_user_page = None
        self.wikibreaks = list()
        self.ambiguous = False

    def contained(self, elem) -> bool:
        """
        Method which checks if the wikibreak is contained into it's talk page or user page

        Args:
            elem ([User]): user retrieved from the talk page or user page
        """
        found = False
        for wb in self.wikibreaks:
            if wb.overlap(elem):
                found = True
                break
        if found:
            self.ambiguous = True

    def to_dict(self) -> dict:
        obj = dict()
        obj['name'] = self.name
        obj['id_talk_page'] = self.id_talk_page
        obj['id_user_page'] = self.id_user_page
        obj['wikibreaks'] = list()
        for wb in self.wikibreaks:
            obj['wikibreaks'].append(wb.to_dict())
        obj['ambiguous'] = self.ambiguous
        return obj

def analyze_revisions(
    rev: dict, 
    wb_actives: dict, 
    values: dict, 
    data: dict) -> dict:
    """
    Method which updates the batch by adding the current user revision

    Args:
        rev (dict): revision
        wb_actives (dict): active wikibreaks
        values (dict): current users' batch
        data (dict): new user data

    Returns:
        values [dict]: the updated users' batch
    """


    if rev['wikibreaks']:
        # all the wb
        all_wb = set()
        
        # all active elements, to find
        for el in wb_actives:
            all_wb.add(el)

        for wb in rev['wikibreaks']: 
            # element found
            if wb['wikibreak_name'] in all_wb:
                all_wb.remove(wb['wikibreak_name'])
            
            # if not present in the wb active dictionary, I need to create it
            from_date = datetime.datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))

            if not wb['wikibreak_name'] in wb_actives:
                params = Parameters(from_date, wb['options'])
                wb_actives[wb['wikibreak_name']] = Wikibreak(from_date, wb['wikibreak_name'], [params], wb['wikibreak_category'], wb['wikibreak_subcategory'])
            else:
                params = Parameters(from_date, wb['options'])
                # update the options
                if wb_actives[wb['wikibreak_name']].options[-1] != params:
                    wb_actives[wb['wikibreak_name']].options.append(params)
            
        to_date = datetime.datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))

        # the one not found -> basically are ended
        for wb in all_wb:
            wb_actives[wb].to_date = to_date
            values[data['title']].wikibreaks.append(copy.deepcopy(wb_actives[wb]))
            del wb_actives[wb]
    else:
        to_date = datetime.datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))
        # the one not found
        for wb in wb_actives:
            wb_actives[wb].to_date = to_date
            values[data['title']].wikibreaks.append(copy.deepcopy(wb_actives[wb]))
        wb_actives.clear()
    return values

def store_batch(
    data: dict, 
    set_analyzed: set, 
    values: dict
    ) -> dict:
    """
    Store batch method, basically store the new user in the values batch

    Args:
        data (dict): new user
        set_analyzed (set): already analyzed users
        values (dict): current users' batch

    Returns:
        values [dict]: updated batch
    """

    # already analyzed in previous iterations
    if data['title'] in set_analyzed:
        return values

    # to save
    if not data['title'] in values:
        # creating the user
        utente = User(data['title'])

        # get the namespace
        if data['namespace'] == 2:
            utente.id_user_page = data['id']
        else:
            utente.id_talk_page = data['id']
        
        # save the user
        values[data['title']] = utente
        
        # wikibreaks which are active
        wb_actives = dict()

        # revisions
        for rev in data['revisions']:
            # analyze user revision
            values = analyze_revisions(rev, wb_actives, values, data)
        
        # not ended elements
        for wb in wb_actives:
            values[data['title']].wikibreaks.append(copy.deepcopy(wb_actives[wb]))
    else:
        
        # getting the namespace
        if data['namespace'] == 2:
            values[data['title']].id_user_page = data['id']
        else:
            values[data['title']].id_talk_page = data['id']
        
        # wikibreaks which are active
        wb_actives = dict()
        
        # revisions
        for rev in data['revisions']:
            values = analyze_revisions(rev, wb_actives, values, data)
        
        # not ended elements
        for wb in wb_actives:
            if not values[data['title']].ambiguous:
                values[data['title']].contained(wb_actives[wb])
            values[data['title']].wikibreaks.append(copy.deepcopy(wb_actives[wb]))

    return values

def update_batch(data: dict):
    """
    Method used in order to update one user within the batch

    Args:
        data (dict): user to update

    Returns:
        values [dict]: updated users' batch
    """

    # get the namespace
    if data['namespace'] == 2:
        values[data['title']].id_user_page = data['id']
    else:
        values[data['title']].id_talk_page = data['id']

    # wikibreaks which are active
    wb_actives = dict()

    # revisions
    for rev in data['revisions']:
        
        # if the revision has wikibreaks
        if rev['wikibreaks']:
            
            # all the wb
            all_wb = set()
            
            # all active elements to find
            for el in wb_actives:
                all_wb.add(el)

            for wb in rev['wikibreaks']:
                # element found
                if wb['wikibreak_name'] in all_wb:
                    all_wb.remove(wb['wikibreak_name'])
                
                from_date = datetime.datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))

                # if not present in the wb active dictionary, I need to create it
                if not wb['wikibreak_name'] in wb_actives:
                    params = Parameters(from_date, wb['options'])
                    wb_actives[wb['wikibreak_name']] = Wikibreak(from_date, wb['wikibreak_name'], [params], wb['wikibreak_category'], wb['wikibreak_subcategory'])
                else:
                    # already present, then update its parameter -> only if the options are different
                    params = Parameters(from_date, wb['options'])
                    # update the options
                    if wb_actives[wb['wikibreak_name']].options[-1] != params:
                        wb_actives[wb['wikibreak_name']].options.append(params)

            to_date = datetime.datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))

            # the ones not found in the iteration: -> have been removed from the page
            for wb in all_wb:
                wb_actives[wb].to_date = to_date
                if not values[data['title']].ambiguous:
                    values[data['title']].contained(wb_actives[wb]) # check if the user is ambiguous
                values[data['title']].wikibreaks.append(copy.deepcopy(wb_actives[wb]))  # new wikibreak
                del wb_actives[wb]  # remove the old one
        else:

            # in that revision the user doesn't have wikibreaks than, the previous active ones have ended
            to_date = datetime.datetime.fromisoformat(rev['timestamp'].replace('Z', '+00:00'))
            # the one not found
            for wb in wb_actives:
                wb_actives[wb].to_date = to_date
                values[data['title']].wikibreaks.append(copy.deepcopy(wb_actives[wb]))
            wb_actives.clear()

    # not ended wikibreaks
    for wb in wb_actives:
        if not values[data['title']].ambiguous:
            values[data['title']].contained(wb_actives[wb])
        values[data['title']].wikibreaks.append(copy.deepcopy(wb_actives[wb]))
    return values

def save_batch(
    n_written: int, 
    start_line: int, 
    values: dict, 
    set_analyzed: set, 
    feature_file: TextIOWrapper) -> Tuple[bool, int, dict, set, int]:
    """
    Method which saves the batch in the output file

    Args:
        n_written (int): element written
        start_line (int): starting line to update
        values (dict): users to write in the output file
        set_analyzed (set): users analyzed
        feature_file (TextIOWrapper): feature file

    Returns:
        Tuple[bool, int, dict, set, int]: respectively:
        stop_analyze, if the analysis has ended
        start_line, new starting line
        values, emptied version of the values dictionary
        set_analyzed, set of analyzed users
        n_written, number of user written in the file
    """

    stop_analyze = False    # if the analysis is finished or not

    for val in values:
        # there has been an error
        if not values[val].wikibreaks:
            print('Error', val, 'not found')
            exit(1)
        values[val].wikibreaks.sort()   # sort the breaks
        # write the file
        feature_file.write(json.dumps(values[val].to_dict(), default=str).encode('utf-8'))
        feature_file.write('\n'.encode('utf-8'))
        n_written += 1  # new user written in the output file
        # add the analyzed version of the file
        set_analyzed.add(val)
    
    values.clear() # empty the values dictionary (batch)

    # the file has ended
    if start_line > line_number:
        stop_analyze = True
    
    # new starting line
    start_line += threshold
    
    print('Analizzare da {}'.format(start_line))

    return stop_analyze, start_line, values, set_analyzed, n_written

def analyze_lines(
    start_line: int, 
    threshold: int, 
    folder: str, 
    filename: str, 
    values: dict, 
    n_written: int,
    set_analyzed: set) -> Tuple[bool, int, dict, int, set]:
    """
    Function which analyze lines in order to produce the refactored version of the merged file

    Args:
        start_line (int): line from which the analysis should start
        threshold (int): how many line to analyze at each iteration
        folder (str): folder in which the data are
        filename (str): filename
        values (dict): batch values
        n_written (int): written elements
        set_analyzed (set): 

    Returns:
        Tuple[bool, int, dict, int, set]:
        -> the file analysis should be stopped
        -> new starting line
        -> processed elements
        -> analyzed users
    """

    stop_analyze = False

    with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
        i = 0           # line index
        for line in f:
            data = json.loads(line.decode('utf-8'))
            if not (i < start_line):
                # save elements within the treshold
                if i <= start_line + threshold:
                    # store value within the batch
                    values = store_batch(data, set_analyzed, values)
                elif data['title'] in values:
                    # update the element within the batch, if already present
                    values = update_batch(data)
            i += 1
        # save the batch
        stop_analyze, start_line, values, set_analyzed, n_written = save_batch(
            n_written, 
            start_line,
            values, 
            set_analyzed, 
            feature_file
        )

    return stop_analyze, start_line, values, n_written, set_analyzed

if __name__ == "__main__":

    folder = sys.argv[1]
    output_folder = sys.argv[2]
    param_name = sys.argv[3]
    param_date = sys.argv[4]

    threshold = 30
    set_analyzed = set()
    n_written = 0
    values = dict()

    if len(sys.argv) < 5:
        print('No arguments provided')
        exit(1)

    # files
    feature_file = gzip.open('{}/{}_{}_refactored_wikibreaks_dataset.json.gz'.format(output_folder, param_name, param_date), 'wb')
    stats_file = gzip.open('{}/{}_{}_refactored_wikibreaks_stats.json.gz'.format(output_folder, param_name, param_date), 'wb')

    for filename in os.listdir(folder):

        try:
            name, date, other = filename.split("_", 2)
        except:
            print('Discarded:', filename)
            continue

        if name == param_name and date == param_date and filename.endswith('dataset.json.gz'):
            line_number = 0
            # total number of lines in the file
            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                line_number = sum(1 for _ in f)
            start_line = 0

            stop_analyze = False

            # analyze the file
            while not stop_analyze:
                stop_analyze, start_line, values, n_written, set_analyzed = analyze_lines(
                    start_line, 
                    threshold, 
                    folder, 
                    filename, 
                    values, 
                    n_written, 
                    set_analyzed
                )
        elif name == param_name and date == param_date and filename.endswith('stats.json.gz'):
            stats_obj = None
            # the statistic file will not be modified
            with gzip.open('{}/{}'.format(folder, filename), 'rb') as f:
                for line in f:
                    stats_file.write(line)
        else:
            continue

    print(len(set_analyzed), n_written)

    feature_file.close()
    stats_file.close()