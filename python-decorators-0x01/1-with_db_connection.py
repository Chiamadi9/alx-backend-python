import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator that opens a sqlite3 connection to 'users.db' when the wrapped
    function is called, injects it as the first positional argument (unless a
    connection is already provided by the caller), and ensures the connection
    is closed after the function returns or raises.
    Usage: decorate functions whose first parameter is `conn`, e.g.
      @with_db_connection
      def get_user_by_id(conn, user_id): ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # If caller provided a connection via keyword 'conn', use it and don't manage it here
        provided_conn = kwargs.get("conn", None)

        # If caller provided a connection positionally (first arg) and it looks like a sqlite3.Connection, use it
        if provided_conn is None and args:
            first_arg = args[0]
            if isinstance(first_arg, sqlite3.Connection):
                provided_conn = first_arg

        if provided_conn is not None:
            # Connection already provided by caller — call function directly
            return func(*args, **kwargs)

        # No connection provided — open one and inject it as the first positional arg
        conn = sqlite3.connect("users.db")
        try:
            # Build new args with conn inserted at front
            new_args = (conn,) + args
            return func(*new_args, **kwargs)
        finally:
            conn.close()

    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

#### Fetch user by ID with automatic connection handling
if __name__ == "__main__":
    user = get_user_by_id(user_id=1)
    print(user)
