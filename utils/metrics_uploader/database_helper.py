import psycopg2
from typing import Optional
import gzip
import bz2

UW_CATEGORY = 'user_warnings'
WB_CATEGORY = 'wikibreak'

class Metric:
    """
    Class which envelope the structure of the metric which will be computed and inserted into the postgres database
    """
    def __init__(self, name: str, year: int, month: int, category: str, uw_category: Optional[str], wikibreak_category1: Optional[str], wikibreak_category2: Optional[str], wikibreak_subcategory: Optional[str], amount: Optional[int] = None, cumulative_amount: Optional[int] = None):
        self.name = name
        self.year = year
        self.month = month
        self.category = category
        self.uw_category = uw_category
        self.wikibreak_category1 = wikibreak_category1
        self.wikibreak_category2 = wikibreak_category2
        self.wikibreak_subcategory = wikibreak_subcategory
        self.amount = amount
        self.cumulative_amount = cumulative_amount

def create_index(connection: psycopg2.extensions.connection, cursor: psycopg2.extensions.cursor):
    """Creates an hash index on the name column

    Args:
        connection (psycopg2.extensions.connection): [description]
        cursor (psycopg2.extensions.cursor): [description]
    """
    create_index_query = "CREATE INDEX template_name_index ON templates USING hash (name)"
    cursor.execute(create_index_query)
    connection.commit()
    print("Index on the column name created successfully")

def output_reader(path: str, compression: Optional[str]):
    """Open data to a compressed file: bz2 and gzip"""
    if compression == '.bz2':
        return bz2.open(path, 'rb')
    elif compression == '.gz':
        return gzip.open(path, 'rb')
    else:
        return open(path, 'r')

def create_table(connection: psycopg2.extensions.connection, cursor: psycopg2.extensions.cursor):
    """Function which creates the table if needed

    Args:
        connection (psycopg2.extensions.connection): database connection
        cursor (psycopg2.extensions.cursor): database cursor
    """
    # SQL query to templates table
    create_table_query = '''CREATE TABLE IF NOT EXISTS templates
          (id                   SERIAL      PRIMARY KEY     NOT NULL,
          name                  TEXT                        NOT NULL,
          year                  INT                         NOT NULL,
          month                 INT                         NOT NULL,
          category              TEXT                        NOT NULL,
          uw_category           TEXT,
          wikibreak_category1   TEXT,
          wikibreak_category2   TEXT,
          wikibreak_subcategory TEXT,
          amount                INT,
          cumulative_amount      INT); 
          '''
    # Execute a command
    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully")


def connect(dbname: str, user:str, password: str, port: str):
    """ Function which connects to the postgres database """
    conn = None
    try:
        # read connection parameters
        params = {'dbname':dbname, 'user':user, 'password':password, 'port':port }

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        
        # create a cursor
        cur = conn.cursor()
        
        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        conn = None
    return conn

def drop_table(connection: psycopg2.extensions.connection, cursor: psycopg2.extensions.cursor):
    """Function which drops the table

    Args:
        connection (psycopg2.extensions.connection): database connection
        cursor (psycopg2.extensions.cursor): database cursor
    """
    # SQL query to drop templates table
    drop_table_query = '''DROP TABLE templates;'''
    # Execute a command
    cursor.execute(drop_table_query)
    connection.commit()
    print("Table deleted successfully")