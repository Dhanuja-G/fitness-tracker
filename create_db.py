import sqlite3

con = sqlite3.connect("fitness.db")
cur = con.cursor()

# USERS TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
password TEXT
)
""")

# FITNESS TABLE WITH DATE
cur.execute("""
CREATE TABLE IF NOT EXISTS fitness(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
exercise TEXT,
duration TEXT,
calories INTEGER,
date TEXT
)
""")

con.commit()
con.close()

print("Database Created Successfully")