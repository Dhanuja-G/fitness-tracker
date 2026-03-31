import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("fitness.db")

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """
)

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS fitness(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        exercise TEXT NOT NULL,
        duration INTEGER NOT NULL,
        calories INTEGER NOT NULL,
        date TEXT NOT NULL
    )
    """
)

con.commit()
cur.close()
con.close()

print(f"SQLite database created successfully at {DB_PATH}")
