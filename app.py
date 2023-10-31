from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Nani@01012004',
    'database': 'dbms_project',
}


def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        print("Connected to the database")
        return connection, cursor
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None


conn, cursor = connect_to_database()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_attendance')
def start_attendance():
    return "Attendance recording started"


@app.route('/manual_attendance')
def manual_attendance():
    return "manual attendance"


@app.route('/check_attendance_range', methods=['POST'])
def check_attendance_range():

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
