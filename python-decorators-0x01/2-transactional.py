import sqlite3
import functools
from datetime import datetime
import os

def with_db_connection(func):
    """
    Opens a sqlite3 connection to 'users.db' when the wrapped function is called,
    injects it as the first positional argument (unless a connection is already provided),
    and ensures the connection is closed after the function returns or raises.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # If a connection was provided by caller, use it
        provided_conn = kwargs.get("conn", None)
        if provided_conn is None and args:
            first_arg = args[0]
            if isinstance(first_arg, sqlite3.Connection):
                provided_conn = first_arg

        if provided_conn is not None:
            return func(*args, **kwargs)

        # Open and inject connection
        conn = sqlite3.connect("users.db")
        try:
            new_args = (conn,) + args
            return func(*new_args, **kwargs)
        finally:
            conn.close()
    return wrapper

def transactional(func):
    """
    Decorator that wraps a function expecting a sqlite3.Connection as its first
    positional argument in a database transaction. If the function raises an
    exception the transaction is rolled back; otherwise it is committed.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Find connection either in kwargs or as the first positional arg
        conn = kwargs.get("conn", None)
        if conn is None and args:
            first_arg = args[0]
            if isinstance(first_arg, sqlite3.Connection):
                conn = first_arg

        # If no connection is available, run function normally (no transaction)
        if conn is None:
            return func(*args, **kwargs)

        # Begin transaction, run function, commit or rollback as needed
        try:
            # Explicit BEGIN helps when using autocommit modes
            conn.execute("BEGIN")
            result = func(*args, **kwargs)
            conn.commit()
            return result
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))

# Update user's email with automatic connection and transaction handling
if __name__ == "__main__":
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
