# Fitness Tracker Web Application

A simple web application to track daily workouts and calories burned.
Users can log exercises, view workout history, and analyze calories using weekly and monthly graphs.

## Technologies Used
- Python
- Flask
- HTML
- CSS
- MySQL
- Chart.js

## Features
- User Login System
- Dashboard
- Add Workout (Exercise, Duration, Calories, Date)
- View Workout History
- Weekly Calories Tracking
- Monthly Calories Tracking
- Graph Visualization of Calories Burned
- Logout Option

## Project Structure
fitness-tracker/
|-- app.py
|-- create_db.py
|-- templates/
|-- static/
`-- README.md

## How to Run the Project

1. Clone the repository

```bash
git clone https://github.com/SudhaReddy9676/fitness-tracker.git
cd fitness-tracker
```

2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies

```powershell
pip install -r requirements.txt
```

4. Set your MySQL connection details

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your_password"
$env:MYSQL_DB="fitness_tracker"
```

5. Create the database and tables

```powershell
python create_db.py
```

6. Run the application

```powershell
python app.py
```

7. Open in browser

`http://127.0.0.1:5000/`
