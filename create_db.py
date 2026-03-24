import os

import mysql.connector

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
}

DATABASE_NAME = os.getenv("MYSQL_DB", "fitness_tracker")

con = mysql.connector.connect(**DB_CONFIG)
cur = con.cursor()

cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}`")
cur.execute(f"USE `{DATABASE_NAME}`")

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS users(
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
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
        exercise VARCHAR(100) NOT NULL,
        duration INT NOT NULL,
        calories INT NOT NULL,
        date DATE NOT NULL
    )
    """
)

con.commit()
cur.close()
con.close()

print("MySQL database and tables created successfully")
