import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, redirect, render_template, request, send_from_directory, session

app = Flask(__name__)
app.secret_key = "fitness_secret_key"

DB_PATH = Path(__file__).with_name("fitness.db")
IMAGE_DIR = Path(__file__).with_name("IMAGES")


def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def create_tables():
    con = get_connection()
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
                "INSERT INTO users(name, email, password) VALUES(?, ?, ?)",
                (name, email, password),
            )
            con.commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
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
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
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
    cur = con.cursor()

    if request.method == "POST":
        exercise = request.form["exercise"]
        duration = request.form["duration"]
        calories = request.form["calories"]
        date = request.form["date"]

        cur.execute(
            """
            INSERT INTO fitness(user_email, exercise, duration, calories, date)
            VALUES(?, ?, ?, ?, ?)
            """,
            (email, exercise, duration, calories, date),
        )
        con.commit()

    cur.execute(
        "SELECT * FROM fitness WHERE user_email=? ORDER BY date DESC",
        (email,),
    )
    workouts = cur.fetchall()

    cur.execute(
        "SELECT SUM(calories) AS total_calories FROM fitness WHERE user_email=?",
        (email,),
    )
    total_row = cur.fetchone()
    total = total_row["total_calories"] if total_row and total_row["total_calories"] else 0

    current_month = datetime.now().strftime("%Y-%m")
    cur.execute(
        """
        SELECT SUM(calories) AS monthly_calories FROM fitness
        WHERE user_email=? AND substr(date, 1, 7) = ?
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
        WHERE user_email=? AND date BETWEEN ? AND ?
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
    cur = con.cursor()

    cur.execute(
        """
        SELECT date, calories FROM fitness
        WHERE user_email=? ORDER BY date
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
        "DELETE FROM fitness WHERE id=? AND user_email=?",
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
