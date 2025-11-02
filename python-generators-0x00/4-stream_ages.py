#!/usr/bin/python3
import mysql.connector

def stream_user_ages(
    host: str = 'localhost',
    user: str = 'root',
    password: str = 'THELordISMyCatch1101?',
    database: str = 'ALX_prodev'
):
    """
    Generator that yields the `age` of each user one by one.
    Uses exactly one loop over the cursor.
    """
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")

    for row in cursor:      # ← Loop 1: streaming ages
        yield row['age']

    cursor.close()
    conn.close()

def calculate_average_age():
    """
    Consumes the age generator to compute the average age
    without loading all ages into memory.
    Uses exactly one loop to accumulate sum and count.
    """
    total_age = 0
    count = 0

    for age in stream_user_ages():    # ← Loop 2: aggregation
        total_age += age
        count += 1

    average = (total_age / count) if count else 0
    print(f"Average age of users: {average:.2f}")

if __name__ == '__main__':
    calculate_average_age()
