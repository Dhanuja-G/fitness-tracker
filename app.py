from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "fitness_secret_key"

def get_connection():
    con = sqlite3.connect("fitness.db")
    con.row_factory = sqlite3.Row
    return con

def create_tables():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fitness(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        exercise TEXT,
        duration INTEGER,
        calories INTEGER,
        date TEXT
    )
    """)

    con.commit()
    con.close()

create_tables()

# REGISTER
@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        con = get_connection()
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                        (name, email, password))
            con.commit()
            return redirect("/login")
        except:
            return "Email already exists!"

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password=?",
                    (email, password))
        user = cur.fetchone()

        if user:
            session["user"] = user["name"]
            session["email"] = user["email"]
            return redirect("/dashboard")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")

# DASHBOARD
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

        cur.execute("""
        INSERT INTO fitness(user_email,exercise,duration,calories,date)
        VALUES(?,?,?,?,?)
        """, (email, exercise, duration, calories, date))
        con.commit()

    cur.execute("SELECT * FROM fitness WHERE user_email=? ORDER BY date DESC",
                (email,))
    workouts = cur.fetchall()

    cur.execute("SELECT SUM(calories) FROM fitness WHERE user_email=?",
                (email,))
    total = cur.fetchone()[0] or 0

    current_month = datetime.now().strftime("%Y-%m")
    cur.execute("""
    SELECT SUM(calories) FROM fitness
    WHERE user_email=? AND date LIKE ?
    """, (email, current_month + "%"))
    monthly = cur.fetchone()[0] or 0

    today = datetime.now()
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)

    cur.execute("""
    SELECT SUM(calories) FROM fitness
    WHERE user_email=? AND date BETWEEN ? AND ?
    """, (email,
          start_week.strftime("%Y-%m-%d"),
          end_week.strftime("%Y-%m-%d")))
    weekly = cur.fetchone()[0] or 0

    con.close()

    return render_template("dashboard.html",
                           name=name,
                           workouts=workouts,
                           total=total,
                           monthly=monthly,
                           weekly=weekly)

# GRAPH PAGE
@app.route("/graph")
def graph():
    if "email" not in session:
        return redirect("/login")

    email = session["email"]
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
    SELECT date, calories FROM fitness
    WHERE user_email=? ORDER BY date
    """, (email,))
    data = cur.fetchall()
    con.close()

    dates = [row["date"] for row in data]
    calories = [row["calories"] for row in data]

    return render_template("graph.html",
                           dates=dates,
                           calories=calories)

# DELETE
@app.route("/delete/<int:id>")
def delete(id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM fitness WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)