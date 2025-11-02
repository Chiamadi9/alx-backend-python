#!/usr/bin/python3
import mysql.connector

def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows from user_data in batches of `batch_size`.
    Yields one list of rows per batch.
    """
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='THELordISMyCatch1101?',
        database='ALX_prodev'
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, email, age FROM user_data")

    # Loop 1: fetch one batch at a time
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch

    cursor.close()
    conn.close()


def batch_processing(batch_size):
    """
    Processes each batch from stream_users_in_batches:
    prints only users over age 25.
    """
    # Loop 2: iterate over batches
    for batch in stream_users_in_batches(batch_size):
        # Loop 3: iterate rows in batch and filter
        for user in batch:
            if user['age'] > 25:
                print(user)
