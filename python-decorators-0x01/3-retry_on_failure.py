import time
import sqlite3
import functools
from datetime import datetime

#### paste your with_db_decorator here

def with_db_connection(func):
    """
    Opens a sqlite3 connection to 'users.db' when the wrapped function is called,
    injects it as the first positional argument (unless a connection is already provided),
    and ensures the connection is closed after the function returns or raises.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        provided_conn = kwargs.get("conn", None)
        if provided_conn is None and args:
            first_arg = args[0]
            if isinstance(first_arg, sqlite3.Connection):
                provided_conn = first_arg

        if provided_conn is not None:
            return func(*args, **kwargs)

        conn = sqlite3.connect("users.db")
        try:
            new_args = (conn,) + args
            return func(*new_args, **kwargs)
        finally:
            conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):
    """
    Decorator factory that retries the wrapped function up to `retries` times
    when it raises an exception. Waits `delay` seconds between attempts.
    Retries the entire wrapped call (including connection management).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if attempt == retries:
                        raise
                    time.sleep(delay)
            # If loop exits unexpectedly, re-raise the last exception
            if last_exc:
                raise last_exc
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure
if __name__ == "__main__":
    users = fetch_users_with_retry()
    print(users)
