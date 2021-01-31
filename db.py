import sqlite3

conn = sqlite3.connect('users.db')

with conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS users (user_id text primary key)''')


async def add_user(user_id: str):
    try:
        with conn:
            conn.execute(f"INSERT INTO users VALUES ({user_id})")

    except sqlite3.IntegrityError:
        print(f'User {user_id} has already been added ')


async def get_all_users():
    return conn.execute(f"SELECT * FROM users")







