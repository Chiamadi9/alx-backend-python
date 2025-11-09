import sqlite3
import functools

#### decorator to log SQL queries

def log_queries():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get the SQL query from kwargs first, then from positional args
            query = kwargs.get("query")
            if query is None and args:
                # assume first positional arg that is a str is the query
                for a in args:
                    if isinstance(a, str):
                        query = a
                        break
            # Fallback if still not found
            if query is None:
                query = "<no query found>"
            print(f"Executing SQL: {query}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@log_queries()
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
print(users)
