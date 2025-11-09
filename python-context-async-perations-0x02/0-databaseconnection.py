import sqlite3

class DatabaseConnection:
    """
    Class-based context manager that opens a sqlite3 connection on enter
    and ensures it is committed (if no exception) or rolled back (on exception),
    then closed on exit.
    Usage:
        with DatabaseConnection("users.db") as conn:
            cursor = conn.cursor()
            ...
    """
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.conn is None:
                return False
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
        finally:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
        return False

# Use the context manager to query and print users
if __name__ == "__main__":
    with DatabaseConnection("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
