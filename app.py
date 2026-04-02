import os
from datetime import datetime, timedelta
from pathlib import Path

import mysql.connector
from flask import Flask, redirect, render_template, request, send_from_directory, session

app = Flask(__name__)
app.secret_key = "fitness_secret_key"

IMAGE_DIR = Path(__file__).with_name("IMAGES")

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "fitness_tracker"),
}


def get_server_connection():
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def create_tables():
    server_con = get_server_connection()
    server_cur = server_con.cursor()
    server_cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    server_cur.close()
    server_con.close()

    con = get_connection()
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


create_tables()


@app.route("/images/<path:filename>")
def images(filename):
    return send_from_directory(IMAGE_DIR, filename)


@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        con = get_connection()
        cur = con.cursor()
        try:
            cur.execute(
                "INSERT INTO users(name, email, password) VALUES(%s, %s, %s)",
                (name, email, password),
            )
            con.commit()
            return redirect("/login")
        except mysql.connector.IntegrityError:
            return "Email already exists!"
        finally:
            cur.close()
            con.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        con = get_connection()
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password),
        )
        user = cur.fetchone()
        cur.close()
        con.close()

        if user:
            session["user"] = user["name"]
            session["email"] = user["email"]
            return redirect("/dashboard")
        return "Invalid Email or Password"

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "email" not in session:
        return redirect("/login")

    name = session["user"]
    email = session["email"]

    con = get_connection()
    cur = con.cursor(dictionary=True)

    if request.method == "POST":
        exercise = request.form["exercise"]
        duration = request.form["duration"]
        calories = request.form["calories"]
        date = request.form["date"]

        cur.execute(
            """
            INSERT INTO fitness(user_email, exercise, duration, calories, date)
            VALUES(%s, %s, %s, %s, %s)
            """,
            (email, exercise, duration, calories, date),
        )
        con.commit()

    cur.execute(
        "SELECT * FROM fitness WHERE user_email=%s ORDER BY date DESC",
        (email,),
    )
    workouts = cur.fetchall()

    cur.execute(
        "SELECT SUM(calories) AS total_calories FROM fitness WHERE user_email=%s",
        (email,),
    )
    total_row = cur.fetchone()
    total = total_row["total_calories"] if total_row and total_row["total_calories"] else 0

    current_month = datetime.now().strftime("%Y-%m")
    cur.execute(
        """
        SELECT SUM(calories) AS monthly_calories FROM fitness
        WHERE user_email=%s AND DATE_FORMAT(date, '%Y-%m') = %s
        """,
        (email, current_month),
    )
    monthly_row = cur.fetchone()
    monthly = (
        monthly_row["monthly_calories"]
        if monthly_row and monthly_row["monthly_calories"]
        else 0
    )

    today = datetime.now()
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)

    cur.execute(
        """
        SELECT SUM(calories) AS weekly_calories FROM fitness
        WHERE user_email=%s AND date BETWEEN %s AND %s
        """,
        (
            email,
            start_week.strftime("%Y-%m-%d"),
            end_week.strftime("%Y-%m-%d"),
        ),
    )
    weekly_row = cur.fetchone()
    weekly = (
        weekly_row["weekly_calories"]
        if weekly_row and weekly_row["weekly_calories"]
        else 0
    )

    cur.close()
    con.close()

    return render_template(
        "dashboard.html",
        name=name,
        workouts=workouts,
        total=total,
        monthly=monthly,
        weekly=weekly,
    )


@app.route("/graph")
def graph():
    if "email" not in session:
        return redirect("/login")

    email = session["email"]
    con = get_connection()
    cur = con.cursor(dictionary=True)

    cur.execute(
        """
        SELECT date, calories FROM fitness
        WHERE user_email=%s ORDER BY date
        """,
        (email,),
    )
    data = cur.fetchall()
    cur.close()
    con.close()

    dates = [row["date"] for row in data]
    calories = [row["calories"] for row in data]

    return render_template("graph.html", dates=dates, calories=calories)


@app.route("/delete/<int:id>")
def delete(id):
    if "email" not in session:
        return redirect("/login")

    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "DELETE FROM fitness WHERE id=%s AND user_email=%s",
        (id, session["email"]),
    )
    con.commit()
    cur.close()
    con.close()
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
