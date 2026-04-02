import os

import mysql.connector

DB_NAME = os.getenv("MYSQL_DATABASE", "fitness_tracker")

SERVER_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
}

DB_CONFIG = {**SERVER_CONFIG, "database": DB_NAME}

server_con = mysql.connector.connect(**SERVER_CONFIG)
server_cur = server_con.cursor()

server_cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
server_cur.close()
server_con.close()

con = mysql.connector.connect(**DB_CONFIG)
cur = con.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS users(
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL
    )
    """
)

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS fitness(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_email VARCHAR(255) NOT NULL,
        exercise VARCHAR(255) NOT NULL,
        duration INT NOT NULL,
        calories INT NOT NULL,
        date DATE NOT NULL
    )
    """
)

con.commit()
cur.close()
con.close()

print(f"MySQL database '{DB_NAME}' and tables created successfully.")
