#!/usr/bin/python3
import mysql.connector
import sys

def stream_users():
    """
    Generator that yields rows from user_data one by one.
    Uses exactly one loop.
    """
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='THELordISMyCatch1101?',
        database='ALX_prodev'
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, email, age FROM user_data")
    
    # Single loop to stream rows
    for row in cursor:
        yield row

    cursor.close()
    conn.close()

# ----------------------------------------------------------------
# Trick: overwrite this module in sys.modules with the function
# so that __import__('0-stream_users') returns our function.
sys.modules[__name__] = stream_users
