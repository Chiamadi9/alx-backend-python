import asyncio
import aiosqlite

DB_PATH = "users.db"

async def async_fetch_users():
    """Fetch all users asynchronously."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.row_factory  # ensure rows behave normally (no-op but keeps pattern)
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return rows

async def async_fetch_older_users(age=40):
    """Fetch users older than the given age asynchronously."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (age,)) as cursor:
            rows = await cursor.fetchall()
            return rows

async def fetch_concurrently():
    """Run both queries concurrently and print their results."""
    all_users_task = async_fetch_users()
    older_users_task = async_fetch_older_users(40)
    all_users, older_users = await asyncio.gather(all_users_task, older_users_task)
    print("All users:")
    for row in all_users:
        print(row)
    print("\nUsers older than 40:")
    for row in older_users:
        print(row)

if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
