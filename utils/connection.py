import pyodbc



def connection():

    '''

    Creates the connection to the server and database, 

    returning the connection that can then be used to run an SQL query

    '''


    connection_string = '''Driver={SQL Server Native Client 11.0};

                           Server=phh-l-prmsql-l1;

                           Database=PROMS_PUBLICATION;

                           Trusted_Connection=yes;'''


    return pyodbc.connect(connection_string)
