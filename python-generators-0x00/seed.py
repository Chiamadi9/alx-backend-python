import csv
import uuid
import mysql.connector
from mysql.connector import Error

def connect_db(host='localhost', user='root', password='THELordISMyCatch1101?'):
    """
    Connects to the MySQL server (no default database).
    """
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )

def create_database(conn, db_name='ALX_prodev'):
    """
    Creates the database ALX_prodev if it does not exist.
    """
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    conn.commit()
    cursor.close()

def connect_to_prodev(host='localhost', user='root', password='THELordISMyCatch1101?', db_name='ALX_prodev'):
    """
    Connects to the ALX_prodev database.
    """
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

def create_table(conn):
    """
    Creates the user_data table if it does not exist, with:
      - user_id CHAR(36) PRIMARY KEY
      - name      VARCHAR(255) NOT NULL
      - email     VARCHAR(255) NOT NULL
      - age       DECIMAL(3,0)   NOT NULL
      - index on user_id
    """
    ddl = """
    CREATE TABLE IF NOT EXISTS user_data (
      user_id CHAR(36)    PRIMARY KEY,
      name    VARCHAR(255) NOT NULL,
      email   VARCHAR(255) NOT NULL,
      age     DECIMAL(3,0) NOT NULL,
      INDEX idx_user_id (user_id)
    ) ENGINE=InnoDB;
    """
    cursor = conn.cursor()
    cursor.execute(ddl)
    conn.commit()
    cursor.close()

def insert_data(conn, data_or_path):
    """
    Inserts each row into user_data if it does not already exist.
    `rows` is an iterable of tuples: (user_id, name, email, age)
    Uses INSERT IGNORE to skip duplicates on user_id.
    """
    # If there is filename, load it
    if isinstance(data_or_path, str):
        rows = load_csv_data(data_or_path)
    else:
        rows = data_or_path

    # Validate that rows is now a list of tuples
    if not isinstance(rows, (list, tuple)) or not all(isinstance(r, tuple) for r in rows):
        raise TypeError("insert_data expects a list/tuple of tuples or a CSV filepath")
    
    sql = """
    INSERT IGNORE INTO user_data (user_id, name, email, age)
    VALUES (%s, %s, %s, %s)
    """
    cursor = conn.cursor()
    cursor.executemany(sql, rows)
    conn.commit()
    cursor.close()

def stream_rows(conn):
    """
    Generator that yields one row at a time from user_data.
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, email, age FROM user_data")
    for row in cursor:
        yield row
    cursor.close()

def load_csv_data(filepath='user_data.csv'):
    """
    Reads user_data.csv and returns a list of tuples:
    (user_id, name, email, age)
    If CSV has no user_id column, generates a UUID for each row.
    """
    rows = []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for rec in reader:
            # If the CSV includes a user_id column, use it; else generate one.
            uid = rec.get('user_id') or str(uuid.uuid4())
            name  = rec['name']
            email = rec['email']
            age   = rec['age']
            rows.append((uid, name, email, age))
    return rows

def main():
    try:
        # 1. Connect to MySQL server, create database
        conn_server = connect_db(password='THELordISMyCatch1101?')
        create_database(conn_server)
        conn_server.close()

        # 2. Connect to ALX_prodev database, create table
        conn = connect_to_prodev(password='THELordISMyCatch1101?')
        create_table(conn)

        # 3. Load data from CSV and insert
        rows = load_csv_data('user_data.csv')
        insert_data(conn, rows)

        # 4. Stream rows one by one and print
        print("Streaming rows from user_data:")
        for record in stream_rows(conn):
            print(record)

        conn.close()

    except Error as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
