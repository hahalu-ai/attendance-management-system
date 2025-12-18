import mysql.connector
from mysql.connector import Error
from ..config import Config

def get_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**Config.get_db_config())
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Execute a database query with proper connection handling

    Args:
        query: SQL query string
        params: Query parameters (tuple)
        fetch_one: Return single row as dictionary
        fetch_all: Return all rows as list of dictionaries
        commit: Commit the transaction

    Returns:
        Query results or None
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())

        if commit:
            conn.commit()
            return cursor.lastrowid

        if fetch_one:
            result = cursor.fetchone()
            return result

        if fetch_all:
            result = cursor.fetchall()
            return result

    except Error as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
