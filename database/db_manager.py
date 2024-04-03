# import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool

class DatabaseManager:
    def __init__(self, host, user, password, database, pool_name="mypool", pool_size=5):
        self.pool = MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            host=host,
            user=user,
            password=password,
            database=database
        )

    def execute_query(self, query, params=None, commit=False):
        result = None
        connection = None
        try:
            connection = self.pool.get_connection()
            if connection.is_connected():
                print("Mysql database connected!")
                cursor = connection.cursor(dictionary=False)
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                if commit:
                    connection.commit()
                    print("Transaction committed.")
                    return 
                else:
                    result = cursor.fetchall()
                    if cursor.description: 
                        dbcols = [desc[0] for desc in cursor.description]
                    else:
                        dbcols = ""
                cursor.close()
        except Error as e:
            if connection:
                connection.rollback()
                print("Transaction rolled back.")
            print(f"Error: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()
                print("MySQL connection is closed.")
        return {
                'dbcols':dbcols,
                'result':result
                }

    def execute_transaction(self, queries):
        connection = None
        try:
            connection = self.pool.get_connection()
            if connection.is_connected():
                print("Mysql database connected!")
                cursor = connection.cursor(dictionary=True)
                # excecute each query in the list of queries
                for query, params in queries:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    result = cursor.fetchall()
                # only commit the transaction if all queries succeed
                connection.commit()
                print("Transaction committed.")
                # close the cursor
                cursor.close()
        # catch any exception and rollback the transaction
        except Error as e:
            if connection:
                # rollback if any exception occured
                connection.rollback()
                print("Transaction rolled back.")
            print(f"Error: {e}")
        finally:
            # close the connection
            if connection and connection.is_connected():
                connection.close()
                print("MySQL connection is closed.")
        return result
