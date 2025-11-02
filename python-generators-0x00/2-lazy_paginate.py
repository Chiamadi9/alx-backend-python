#!/usr/bin/python3
import seed

def paginate_users(page_size, offset):
    """
    Fetches a single page of rows from user_data using LIMIT/OFFSET.
    Returns a list of dicts.
    """
    conn = seed.connect_to_prodev()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM user_data "
        f"LIMIT {page_size} OFFSET {offset}"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def lazy_pagination(page_size):
    """
    Generator that lazily yields pages of users (each a list of rows).
    Uses exactly one loop to fetch pages until none remain.
    """
    offset = 0
    while True:                      # ← Single loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
