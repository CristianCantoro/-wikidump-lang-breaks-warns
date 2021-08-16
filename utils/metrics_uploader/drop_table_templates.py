

import sys
from database_helper import connect, drop_table
from psycopg2.extensions import connection

def main(connection: connection):
    """
    Function which deletes the current table
    """

    if not connection:
        print('It is not possible to establish a connection to the postgres database, therefore the process could not continue.')
        exit(1)

    # Get the cursor connection
    cursor = connection.cursor()
    # create the table
    drop_table(connection, cursor)
    # close the cursor
    cursor.close()
    # close the connection
    connection.close()

if __name__ == '__main__':
    """
    Main function:
        -   sys.argv[1]:    database name
        -   sys.argv[2]:    dataset user
        -   sys.argv[3]:    password
        -   sys.argv[4]:    port
    """
    if len(sys.argv) <= 4:
        print('The database name, user, password and port is a required input')
        exit(0)
    connection = connect(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print('Executing main...')
    main(connection)