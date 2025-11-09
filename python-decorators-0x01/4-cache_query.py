import time
import sqlite3
import functools
import threading
from datetime import datetime

# Simple in-memory cache mapping SQL query string -> (result, timestamp)
query_cache = {}
_cache_lock = threading.Lock()
CACHE_TTL = 300  # seconds; optional TTL to expire cached entries

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

def cache_query(func):
    """
    Decorator that caches results of functions whose SQL query string is passed
    as a parameter named 'query' or as the second positional argument (after conn).
    The cache key is the SQL string. Thread-safe and supports optional TTL.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the SQL query string from kwargs or positional args.
        query = kwargs.get("query", None)

        # If the function is wrapped by with_db_connection, the first positional
        # argument will be conn and the query will be args[1]
        if query is None:
            # Look for a str query in positional args (skip sqlite3.Connection if present)
            for i, a in enumerate(args):
                if isinstance(a, str):
                    query = a
                    break

        if query is None:
            # No query found; just call the function directly (can't cache)
            return func(*args, **kwargs)

        now = time.time()
        # Check cache
        with _cache_lock:
            entry = query_cache.get(query)
            if entry:
                result, ts = entry
                if CACHE_TTL is None or (now - ts) < CACHE_TTL:
                    return result
                else:
                    # expired
                    del query_cache[query]

        # Not cached -> call the function and store result
        result = func(*args, **kwargs)

        # Store a shallow copy if it's a list of rows to avoid accidental mutation issues
        cached_result = result
        with _cache_lock:
            query_cache[query] = (cached_result, now)

        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
if __name__ == "__main__":
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print("First call, fetched:", users)

    #### Second call will use the cached result
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print("Second call (cached), fetched:", users_again)
