from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart  # Add this import
from email.mime.text import MIMEText
import openpyxl
import subprocess
import psutil
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import os
import matplotlib.pyplot as plt
process_pid = None
process = None


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


def send_email_to_students(course_id, minimum_attendance_percentage):
    cursor.execute("SELECT s.student_id,s.name,s.email, (COUNT(CASE WHEN a.status = 'present' THEN 1 ELSE NULL END) * 100.0 / COUNT(*)) AS percentage FROM student s join attendance a on s.student_id=a.student_id WHERE a.course_id = %s GROUP BY student_id HAVING percentage<%s", (course_id, minimum_attendance_percentage))
    results = cursor.fetchall()

    for student_id, student_name, email, attendance_percentage in results:
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = 'khyathi2003kotipalli@gmail.com'
        sender_password = 'awsn iuvr rkof rztm'

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = 'Attendance Warning'
        body = f"Dear {student_name},\n\nYour attendance percentage for the course {course_id}is below the specified percentage.\n\n Please ensure to attend the upcoming classes to improve your attendance percentage."
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port, timeout=40) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        print(f"Email sent to {email}")


@app.route("/send_mail.html", methods=['GET', 'POST'])
def send_mail():
    if request.method == 'POST':
        course_id = request.form['course_id']
        minimum_attendance_percentage = float(
            request.form['minimum_attendance_percentage'])
        send_email_to_students(course_id, minimum_attendance_percentage)
        status = "Mail sent"
        return render_template('send_mail.html', status=status)

    return render_template('send_mail.html', status="")


def get_course_id(cursor, time):
    day_of_week = datetime.now().strftime('%A')
    fetch_course_id_query = "SELECT course_id FROM timetable WHERE day = %s AND %s BETWEEN start_time AND end_time"
    cursor.execute(fetch_course_id_query, (day_of_week, time))
    course_id_result = cursor.fetchone()
    if course_id_result:
        return course_id_result[0]
    else:
        return None


def is_existing_student(cursor, student_id, course_id, date):
    check_query = "SELECT * FROM attendance WHERE student_id = %s AND course_id = %s AND date = %s"
    cursor.execute(check_query, (student_id, course_id, date))
    existing_entry = cursor.fetchone()
    if existing_entry:
        return existing_entry
    else:
        return False


def mark_absent(conn, cursor, student_id, course_id, date, time):
    if not is_existing_student(cursor, student_id, course_id, date):
        attendance_insert_query = "INSERT INTO attendance (student_id, course_id, date, time, status) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(attendance_insert_query,
                       (student_id, course_id, date, time, "absent"))
        conn.commit()


def mark_all_absent(conn, cursor, course_id, date):
    current_time = datetime.now().time().strftime('%H:%M:%S')
    student_query = "SELECT student_id FROM student"
    cursor.execute(student_query)
    students = cursor.fetchall()
    for student in students:
        student_id = student[0]
        mark_absent(conn, cursor, student_id, course_id, date, current_time)


def print_absentees(cursor, course_id, date):
    print_absenties_query = "SELECT student_id FROM attendance WHERE course_id = %s AND date = %s AND status = %s"
    cursor.execute(print_absenties_query, (course_id, date, "absent"))
    absent_entries = cursor.fetchall()
    return absent_entries


@app.route("/record_attendance.html", methods=['GET', 'POST'])
def record_attendance():

    return render_template('record_attendance.html')


@app.route('/start_recording')
def start_recording():
    global process
    current_date = datetime.now().date()
    current_time = datetime.now().time().strftime('%H:%M:%S')
    course_id = get_course_id(cursor, current_time)
    if course_id:
        print(course_id)
        mark_all_absent(conn, cursor, course_id, current_date)
        print("Recording attendance, press 'q' to terminate")
        process = subprocess.Popen(['python', 'record_attendance.py'])
        process_pid = process.pid
        print(course_id, process_pid)
    return render_template('record_attendance.html')


@ app.route('/stop_recording')
def stop_recording():
    current_date = datetime.now().date()
    current_time = datetime.now().time().strftime('%H:%M:%S')
    course_id = get_course_id(cursor, current_time)
    global process
    process.terminate()
    # absentees = ['test']
    # if process_pid:os.kill(process_pid, 15)
    absentees = []
    absent_entries = print_absentees(cursor, course_id, current_date)
    for entry in absent_entries:
        absentees.append(entry[0])
    print(absentees)
    return render_template('record_attendance.html', absentees=absentees)


@app.route('/check_attendance_range.html', methods=['GET', 'POST'])
def check_attendance_range():
    if request.method == 'POST':
        course_id = request.form['course_id']
        minimum_percentage = float(request.form['minimum_percentage'])
        maximum_percentage = float(request.form['maximum_percentage'])

        cursor.execute("SELECT student_id, (COUNT(CASE WHEN status = 'present' THEN 1 ELSE NULL END) * 100.0 / COUNT(*)) AS percentage FROM attendance WHERE course_id = %s GROUP BY student_id HAVING percentage BETWEEN %s AND %s",
                       (course_id, minimum_percentage, maximum_percentage))
        results = cursor.fetchall()

        if results:
            students = [{'student_id': student, 'percentage': round(
                percentage, 2)} for student, percentage in results]
        else:
            students = []

        return render_template('check_attendance_range.html', students=students)

    return render_template('check_attendance_range.html', students=[])


@app.route("/manual_attendance.html", methods=['GET', 'POST'])
def manual_attendance():
    if request.method == 'POST':
        course_id = request.form['course_id']
        date = str(request.form['date_to_modify'])
        student_id = str(request.form['student_id'])
        get_status_query = "SELECT status FROM attendance WHERE student_id = %s AND course_id = %s AND date = %s;"
        cursor.execute(get_status_query, (student_id, course_id, date))
        status_result = cursor.fetchall()
        return render_template('manual_attendance.html', status=status_result)
    return render_template('manual_attendance.html', status=[])


@app.route("/modify_attendance", methods=['GET', 'POST'])
def modify_attendance():
    if request.method == 'POST':
        course_id = request.form['course_id']
        date = str(request.form['date_to_modify'])
        student_id = str(request.form['student_id'])
        new_status = request.form['status']
        print("hii", date)
        update_attendance_query = "UPDATE attendance SET status = %s WHERE student_id = %s AND course_id = %s AND date = %s;"

        cursor.execute(update_attendance_query,
                       (new_status, student_id, course_id, date))
        print("Attendance modified successfully!")
        get_status_query = "SELECT status FROM attendance WHERE student_id = %s AND course_id = %s AND date = %s;"
        cursor.execute(get_status_query, (student_id, course_id, date))
        status_result = cursor.fetchall()
        print(student_id, "\t", status_result[0][0])
        return render_template('manual_attendance.html')
    return render_template('manual_attendance.html')


@app.route("/particular_day_attendance.html", methods=['GET', 'POST'])
def check_particular_day_attendance():
    if request.method == 'POST':
        date = str(request.form['date_to_check'])
        course_id = request.form['course_id']
        cursor.execute(
            "select student_id, status from attendance where date = %s AND course_id = %s", (date, course_id))
        result = cursor.fetchall()
        present_students = []
        absent_students = []
        for student_id, status in result:
            if status == "present":
                present_students.append(student_id)
            elif status == "absent":
                absent_students.append(student_id)
        students = []
        students.append(present_students)
        students.append(absent_students)
        return render_template('particular_day_attendance.html', students=students)
    return render_template('particular_day_attendance.html', students=[])


@app.route("/particular_student_attendance.html", methods=['GET', 'POST'])
def check_particular_student_attendance():
    if request.method == 'POST':
        course_id = request.form['course_id']
        date = str(request.form['date_to_check'])
        student_id = request.form['student_id']
        existing_record = is_existing_student(
            cursor, student_id, course_id, date)
        if existing_record:
            students = []
            print(existing_record[4])
            students.append("")
            students.append(existing_record[4])
            return render_template('particular_student_attendance.html', students=students)
        else:
            students = []
            print("No record found")
            students.append("student id not found")
            students.append("")
            return render_template('particular_student_attendance.html', students=students)
    return render_template('particular_student_attendance.html')


@app.route("/attendance_trend_chart.html", methods=['GET', 'POST'])
def attendance_trend_chart():
    if request.method == 'POST':
        course_id = request.form['course_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        date_range_attendance_query = """
                    SELECT date,
                    SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_count,
                    SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent_count
                FROM
                    attendance
                WHERE
                    course_id = %s AND
                    date BETWEEN %s AND %s
                GROUP BY
                    date
                ORDER BY
                    date;
                """
        cursor.execute(date_range_attendance_query,
                       (course_id, start_date, end_date))
        data = cursor.fetchall()
        df = pd.DataFrame(
            data, columns=['date', 'present_count', 'absent_count'])
        img_path = "static/Images/plot.png"

        plt.figure(figsize=(8, 6))
        plt.plot(df['date'], df['present_count'], label='Present', marker='o')
        plt.plot(df['date'], df['absent_count'], label='Absent', marker='o')
        plt.xlabel('Date')
        plt.ylabel('Number of Students')
        plt.title(f'Attendance from {start_date} to {end_date}')
        plt.subplots_adjust(bottom=0.2)
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        for i, row in df.iterrows():
            plt.text(row['date'], row['present_count']+2,
                     str(row['present_count']), ha='center', va='top', fontsize=8)
            plt.text(row['date'], row['absent_count']+2,
                     str(row['absent_count']), ha='center', va='top', fontsize=8)
        plt.savefig(img_path, format='png')

        plt.close()
        return render_template('attendance_trend_chart.html', image_path="Images/plot.png")

    return render_template('attendance_trend_chart.html', image_path="")


@app.route("/create_attendance_excel.html", methods=['GET', 'POST'])
def create_attendance_excel():
    if request.method == 'POST':
        start_date = str(request.form['start_date'])
        end_date = str(request.form['end_date'])
        course_id = request.form['course_id']

        start_date = start_date.replace(":", "-")
        end_date = end_date.replace(":", "-")

        file_name = f"{course_id}attendance{start_date}to{end_date}.xlsx"

        query = """
        SELECT 
            a.student_id, 
            s.name AS student_name, 
            s.email AS student_email, 
            COUNT(*) AS total_classes_conducted,
            SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS classes_attended
        FROM attendance a
        JOIN student s ON a.student_id = s.student_id
        WHERE a.course_id = %s AND a.date BETWEEN %s AND %s
        GROUP BY a.student_id;
        """

        cursor.execute(query, (course_id, start_date, end_date))
        attendance_data = cursor.fetchall()
        # print("hiii",attendance_data)
        if not attendance_data:
            status = "No attendance records found for the specified date range."
            return render_template('create_attendance_excel.html', status=status)
        else:
            df = pd.DataFrame(
                attendance_data,
                columns=[
                    "Student ID",
                    "Student Name",
                    "Student Email",
                    "Total Classes Conducted",
                    "Classes Attended"
                ]
            )

            df["Attendance Percentage"] = (
                df["Classes Attended"] / df["Total Classes Conducted"]) * 100
            df = df.sort_values(by="Attendance Percentage", ascending=False)

            wb = Workbook()
            ws = wb.active

            for col_num, column_title in enumerate(df.columns, 1):
                ws.cell(row=1, column=col_num, value=column_title)

            for record in df.to_records(index=False):
                ws.append(list(record))

            wb.save(file_name)

            status = (
                f"Student attendance performance excel sheet for {course_id} between {start_date} and {end_date} has been saved to '{file_name}'.")

            return render_template('create_attendance_excel.html', status=status)
    return render_template('create_attendance_excel.html', status=[])


@app.route("/generate_monthly_attendance.html", methods=['GET', 'POST'])
def generate_monthly_attendance():
    if request.method == 'POST':
        course_id = request.form['course_id']
        year = request.form['year']
        month = request.form['month']
        start_date = f"{year}-{month}-01"
        end_date = f"{year}-{month}-31"
        report_query = """
        SELECT student_id, COUNT(*) AS total_classes, 
            SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) AS attended_classes
        FROM attendance
        WHERE course_id = %s AND date BETWEEN %s AND %s
        GROUP BY student_id;
        """
        cursor.execute(report_query, (course_id, start_date, end_date))
        report_data = cursor.fetchall()
        report = []
        for result in report_data:
            row = []
            row.append(result[0])
            row.append(result[1])
            row.append(result[2])
            attendance_percentage = (result[2] / result[1]) * 100
            attendance_percentage = "{:.2f}".format(attendance_percentage)
            row.append(attendance_percentage)
            report.append(row)
        # print(report)

        return render_template('generate_monthly_attendance.html', report=report)
    return render_template('generate_monthly_attendance.html')


if __name__ == "__main__":
    app.run(debug=True)
