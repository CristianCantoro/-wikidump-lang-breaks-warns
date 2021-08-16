import sys
import json
import pathlib
from datetime import datetime
from collections import OrderedDict
from database_helper import Metric, output_reader, UW_CATEGORY, create_table, connect, create_index
from psycopg2.extensions import connection, cursor

def upload_metrics(connection: connection, cursor: cursor, metrics: list[Metric]):
    """
    Insert the metrics straight into the database

    Args:
        cursor (cursor): database cursor
        metrics (list[Metric]): list of metrics
    """
    for metric in metrics:
        cursor.execute("INSERT INTO templates (name, year, month, category, uw_category, amount, cumulative_amount) VALUES ('{}', {}, {}, '{}', '{}', {}, {})".format(metric.name, metric.year, metric.month, metric.category, metric.uw_category, metric.amount, metric.cumulative_amount))
    connection.commit()
    print("Metrics updated successfully")  

def compute_metrics(dataset_location: str):
    """Function which computes the metrics which will be inserted into the database

    Args:
        dataset_location (str): path of the dataset location

    Returns:
        list(Metric): list of the computed metrics
    """

    # constructing the pandas dataframe
    ########################################

    df: list[dict] = list()
    template_category_mapping: dict = dict()

    with output_reader(dataset_location, pathlib.Path(dataset_location).suffix) as json_file:      
        for i, l in enumerate(json_file.readlines()):
            raw_obj = json.loads(l.decode('utf-8'))['user_warnings_received']

            for raw_line in raw_obj:

                # skipping the non translcluded elements since they do not have any parameter associated, therefore they do not have a date associated
                if not raw_line['transcluded']:
                    continue

                # processing the line which has been read just yet
                del raw_line['transcluded']
                
                # extracting the date in the following format: one field for the year and one field for the month
                if raw_line['parameters']:
                    tmp_date = datetime.fromisoformat(raw_line['parameters'][0]['timestamp'].replace('Z', '+00:00'))
                    raw_line['year'] = int(tmp_date.year)
                    raw_line['month'] = int(tmp_date.month)
                else:
                    raw_line['year'] = None
                    raw_line['month'] = None
                
                del raw_line['parameters']

                # append the newly refactored line
                df.append(raw_line)

                # appending the user warning mapping category
                template_category_mapping[raw_line['user_warning_name']] = raw_line['category']

                if i > 0 and i % 100000 == 0:
                    print('I have analyzed {} lines so far'.format(i))

    # building the counter
    ##########################################
    template_count: dict = dict()

    # preparing the metrics
    for line in df:
        if not line['user_warning_name'] in template_count:
            template_count[line['user_warning_name']] = OrderedDict()
        
        if not line['year'] in template_count[line['user_warning_name']]:
            template_count[line['user_warning_name']][line['year']] = OrderedDict()

        if not line['month'] in template_count[line['user_warning_name']][line['year']]:
            template_count[line['user_warning_name']][line['year']][line['month']] = 0

        # new received user warning found
        template_count[line['user_warning_name']][line['year']][line['month']] += 1

    # deleting the dataframe, it will not be used
    del df

    # Metrics
    metrics: list[Metric] = list()

    # inserting the metrics with the computation of each cumulative amount
    for template in template_count:
        cumulative_amount = 0
        # I am focused on a single template type
        for year in template_count[template]:
            for month in template_count[template][year]:
                cumulative_amount += template_count[template][year][month]
                metrics.append( Metric(name=template, year=year, month=month, category=UW_CATEGORY, 
                                uw_category=template_category_mapping[template], wikibreak_category1=None,
                                wikibreak_category2=None, wikibreak_subcategory=None,
                                amount=template_count[template][year][month], cumulative_amount=cumulative_amount)
                )
            
    return metrics

def main(dataset_location: str, connection: connection):
    """
    Function which takes the connection to the Postgres database as input
    and after having produced the metrics, it uploades them in the following format:
    """

    if not connection:
        print('It is not possible to establish a connection to the postgres database, therefore the process could not continue.')
        exit(1)

    # Get the cursor connection
    cursor = connection.cursor()
    # create the table
    create_table(connection, cursor)
    # compute the metrics
    metrics: list[Metric] = compute_metrics(dataset_location)
    # upload the metrics
    upload_metrics(connection, cursor, metrics)
    # Create index
    create_index(connection, cursor)
    # close the cursor
    cursor.close()
    # close the connection
    connection.close()

if __name__ == '__main__':
    """
    Main function:
        -   sys.argv[1]:    dataset location
        -   sys.argv[2]:    database name
        -   sys.argv[3]:    dataset user
        -   sys.argv[4]:    password
        -   sys.argv[5]:    port
    """
    if len(sys.argv) <= 5:
        print('The dataset location, database name, user, password and port is a required input')
        exit(0)
    connection = connect(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    print('Executing main...')
    main(sys.argv[1], connection)