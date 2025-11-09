import sqlite3
import functools
from datetime import datetime

#### decorator to log SQL queries

def log_queries(func=None):
    """
    Decorator that logs the SQL query string passed to the wrapped function.
    Can be used as @log_queries or @log_queries().
    It looks for a 'query' keyword argument first, then for the first str positional argument.
    If no query string is found it logs '<no query found>'.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            query = kwargs.get("query")
            if query is None:
                # assume first positional arg that is a str is the query
                for a in args:
                    if isinstance(a, str):
                        query = a
                        break
            # Fallback if still not found
            if query is None:
                query = "<no query found>"
            print(f"Executing SQL: {query}")
            return f(*args, **kwargs)
        return wrapper

    if callable(func):
        return decorator(func)
    return decorator

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print(users)

