import os

import pymysql
from dotenv import load_dotenv
from flask import g

# Load environment variables from .env file
load_dotenv()

# Retrieve the environment variables
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")


class DataAccessObject:
    """
    The following Database operations are defined in this class:
       - Set:         Setting a key-value pair in the specified namespace
       - Get:         Getting a value for a given key in specified namespace
       - Delete:      Deleting an entry by namespace and key
       - Count:       Counts the instances of specified value in requested namespace
       - CountGlobal: Counts the instances of specified value across namespaces

    A new DB connection is established and closed upon each request.
    """

    def get_connection(self):
        """
        If no existing connector found in Flask's global context, creates a new DB connector.
        """
        if not hasattr(g, "db_connector"):
            g.db_connector = pymysql.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name,
            )
            print("\nDB connection initialized.")
        return g.db_connector

    def close(self):
        """
        If a connector exists, closes the connector to ensure DB resources are freed.
        """
        connection = self.get_connection()
        try:
            if connection:
                connection.close()
                print("DB connection closed.\n")
        except Exception as e:
            print(f"Error closing connection: {e}")

    def set(self, namespace, key, value):
        """
        Inserts or update a key-value pair in the database.
        If a key doesn't exist in the specified namespace, inserts the entry into the table. Otherwise, updates the existing entry with given value.

        Returns:
           None:      No return is necessary upon a successful commit to DB.
           Exception: DB commit exception thrown if any.
        """

        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                existing_value = self.get(namespace, key)
                if existing_value is None:
                    query = """
                        INSERT INTO storage (`namespace`, `key`, `value`)
                        VALUES (%s, %s, %s)
                    """
                    print(
                        f"Success inserting key {key} and value {value} in namespace {namespace}."
                    )
                    cursor.execute(query, (namespace, key, value))
                else:
                    query = """
                        UPDATE storage
                        SET `value` = %s
                        WHERE `namespace` = %s AND `key` = %s
                    """
                    print(
                        f"Success updating value to {value} for key {key} in namespace {namespace}."
                    )
                    cursor.execute(query, (value, namespace, key))
                connection.commit()

        except Exception as e:
            print(f"Error during insert/update: {e}")
            connection.rollback()
            raise e

    def get(self, namespace, key):
        """
        Retrieves a value for a given namespace and key.

        Returns:
            String:     Value
            Exception:  DB commit exception thrown if any.
        """

        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                retrieve_query = """
                    SELECT `value` FROM STORAGE
                    WHERE `namespace` = %s AND `key` = %s
                """
                cursor.execute(retrieve_query, (namespace, key))
                result = cursor.fetchone()

                if result:
                    print(
                        f"Success retrieving value for key {key} in namespace {namespace}."
                    )
                    return result[0]  # corresponds to value
                else:
                    print(
                        f"No existing entry found for key {key} in namespace {namespace}."
                    )
                    return None

        except Exception as e:
            print(f"Error during retrieve: {e}")
            raise e

    def delete(self, namespace, key):
        """
        Retrieves a value for a given namespace and key.

        Returns:
            String:     Value
            Exception:  DB commit exception thrown if any.
        """

        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                existing_value = self.get(namespace, key)
                if existing_value:
                    query = """
                        DELETE FROM storage 
                        WHERE `namespace` = %s 
                        AND `key` = %s AND `value` = %s
                    """
                    print(
                        f"Success deleting key {key} and value {existing_value} from namespace {namespace}."
                    )
                    cursor.execute(query, (namespace, key, existing_value))
                    connection.commit()
                    return existing_value
                else:
                    print(
                        f"No existing entry found for key {key} in namespace {namespace}."
                    )
                    return None

        except Exception as e:
            print(f"Error during retrieve: {e}")
            raise e

    def count(self, namespace, value):
        """
        Returns the number of instances of value in specified namespace.

        Returns:
            Int:       Count of value in namespace
            Exception: DB commit exception thrown if any.
        """

        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                retrieve_query = """
                    SELECT COUNT(`value`) FROM STORAGE
                    WHERE `namespace` = %s AND `value` = %s
                """
                cursor.execute(retrieve_query, (namespace, value))
                result = cursor.fetchall()

                print(
                    f"Success getting count of value {value} in namespace {namespace}."
                )
                return result[0][0]  # corresponds to count

        except Exception as e:
            print(f"Error during retrieve: {e}")
            raise e

    def count_global(self, value):
        """
        Returns the number of instances of value in across namespaces.

        Returns:
            Int:       Total count of value
            Exception: DB commit exception thrown if any.
        """

        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                retrieve_query = """
                    SELECT COUNT(*) FROM STORAGE
                    WHERE `value` = %s
                """
                cursor.execute(retrieve_query, (value))
                result = cursor.fetchall()

                print(f"Success getting count of value {value}.")
                return result[0][0]  # corresponds to count

        except Exception as e:
            print(f"Error during retrieve: {e}")
            raise e
