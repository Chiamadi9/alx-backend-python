import sqlite3

class ExecuteQuery:
    """
    Context manager that opens a sqlite3 connection to the given database,
    executes the provided query with parameters on enter, and returns the
    fetched results. Ensures the connection is closed and transaction is
    committed or rolled back on exit.
    Usage:
        with ExecuteQuery("users.db", "SELECT ...", (params,)) as results:
            ...
    """
    def __init__(self, db_path, query, params=None):
        self.db_path = db_path
        self.query = query
        self.params = params or ()
        self.conn = None
        self.results = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        cur = self.conn.cursor()
        cur.execute(self.query, self.params)
        # fetch all results and store them; caller receives the list
        self.results = cur.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.conn:
                if exc_type is not None:
                    try:
                        self.conn.rollback()
                    except Exception:
                        pass
                else:
                    try:
                        self.conn.commit()
                    except Exception:
                        pass
                try:
                    self.conn.close()
                except Exception:
                    pass
        finally:
            self.conn = None
        # propagate exceptions to the caller
        return False

# Use the context manager to run the requested query and print results
if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)

    with ExecuteQuery("users.db", query, params) as results:
        for row in results:
            print(row)
