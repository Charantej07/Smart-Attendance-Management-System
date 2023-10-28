import openpyxl
import subprocess
import mysql.connector
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import matplotlib.pyplot as plt

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


def get_course_id(cursor, date, time):
    day_of_week = date.strftime('%A')
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
    print("Absentees list")
    for entry in absent_entries:
        print(entry[0])


def generate_monthly_attendance_report(cursor):
    course_id = input(
        "Enter the course ID for which you want to generate the report: ")
    year = input("Enter the year (YYYY) for the report: ")
    month = input("Enter the month (MM) for the report: ")
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
    print("\nMonthly Attendance Report:")
    print("Student ID\tTotal Classes\tAttended Classes\tAttendance Percentage")
    for row in report_data:
        student_id, total_classes, attended_classes = row
        attendance_percentage = (attended_classes / total_classes) * 100
        print(
            f"{student_id}\t{total_classes}\t{attended_classes}\t{attendance_percentage:.2f}%")


def manual_attendance(cursor, conn):
    course_id = input("Enter course id: ")
    date = input(
        'Enter the date on which attendance has to be modified (YYYY-MM-DD): ')
    student_id = input("Enter the roll number of the student: ")
    get_status_query = "SELECT status FROM attendance WHERE student_id = %s AND course_id = %s AND date = %s;"
    cursor.execute(get_status_query, (student_id, course_id, date))
    status_result = cursor.fetchall()
    print(student_id, "\t", status_result[0][0])
    print("Enter P to mark as present \ A to mark as absent: ")
    update_attendance_query = "UPDATE attendance SET status = %s WHERE student_id = %s AND course_id = %s AND date = %s;"
    choice = 'x'
    valid_choices = ['p', 'P', 'a', 'A']
    while choice not in valid_choices:
        choice = input()
        if choice in ['P', 'p']:
            status = 'present'
        elif choice in ['A', 'a']:
            status = 'absent'
        else:
            print("Enter a valid input")
    cursor.execute(update_attendance_query,
                   (status, student_id, course_id, date))
    print("Attendance modified successfully!")
    cursor.execute(get_status_query, (student_id, course_id, date))
    status_result = cursor.fetchall()
    print(student_id, "\t", status_result[0][0])
    conn.commit()


def check_attendance_range(cursor):
    course_id = input("Enter the course ID: ")
    minimum_percentage = float(input("Enter the minimum percentage: "))
    maximum_percentage = float(input("Enter the maximum percentage: "))
    cursor.execute("SELECT student_id, (COUNT(CASE WHEN status = 'present' THEN 1 ELSE NULL END) * 100.0 / COUNT(*)) AS percentage FROM attendance WHERE course_id = %s GROUP BY student_id HAVING percentage BETWEEN %s AND %s",
                   (course_id, minimum_percentage, maximum_percentage))
    results = cursor.fetchall()
    if results:
        print("Students within the attendance percentage range:")
        for student, percentage in results:
            print(f"Student ID: {student}, Percentage: {percentage:.2f}%")
    else:
        print("No students found within the specified range.")


def check_particular_day_attendance(cursor):
    date = input("Enter the date (YYYY-MM-DD): ")
    course_id = input("Enter the course ID: ")
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
    print("Students present on", date, "for Course", course_id)
    for student_id in present_students:
        print(student_id)
    print("\nStudents absent on", date, "for Course", course_id)
    for student_id in absent_students:
        print(student_id)


def send_mail(cursor):
    course_id = input("Enter the course ID: ")
    minimum_attendance_percentage = float(
        input("Enter the minimum attendance percentage: "))
    cursor.execute("SELECT s.student_id,s.name,s.email, (COUNT(CASE WHEN a.status = 'present' THEN 1 ELSE NULL END) * 100.0 / COUNT(*)) AS percentage FROM student s join attendance a on s.student_id=a.student_id WHERE a.course_id = %s GROUP BY student_id HAVING percentage<%s", (course_id, minimum_attendance_percentage))
    results = cursor.fetchall()

    for student_id, student_name, email, attendance_percentage in results:
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = 'khyathi2003kotipalli@gmail.com'
        sender_password = 'xwkh murg aljh kxlq'

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = 'Attendance Warning'
        body = f"Dear {student_name},\n\nYour attendance percentage for the course {course_id}is below the specified percentage.\n\n Please ensure to attend the upcoming classes to improve your attendance percentage."
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        print(f"Email sent to {email}")


def plot_graph(cursor):
    course_id = input("Enter course id: ")
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")

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
    df = pd.DataFrame(data, columns=['date', 'present_count', 'absent_count'])

    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['present_count'], label='Present', marker='o')
    plt.plot(df['date'], df['absent_count'], label='Absent', marker='o')

    plt.xlabel('Date')
    plt.ylabel('Number of Students')
    plt.title(f'Attendance from {start_date} to {end_date}')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)

    for i, row in df.iterrows():
        plt.text(row['date'], row['present_count']+2,
                 str(row['present_count']), ha='center', va='top', fontsize=8)
        plt.text(row['date'], row['absent_count']+2,
                 str(row['absent_count']), ha='center', va='top', fontsize=8)

    plt.show()


def create_attendance_excel(cursor):
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")
    course_id = input("Enter the course ID: ")

    start_date = start_date.replace(":", "-")
    end_date = end_date.replace(":", "-")

    file_name = f"{course_id}_attendance_{start_date}_to_{end_date}.xlsx"

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

    if not attendance_data:
        print("No attendance records found for the specified date range.")
        return

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

    print(
        f"Student attendance performance excel sheet for {course_id} between {start_date} and {end_date} has been saved to '{file_name}'.")


def main():
    conn, cursor = connect_to_database()
    if conn is None:
        return

    current_date = datetime.now().date()
    current_time = datetime.now().time().strftime('%H:%M:%S')

    while True:
        print("\nMenu Options:")
        print("1. Start Attendance Recording ")
        print("2. Enter Attendance Manually")
        print("3. Details of students with attendance in a particular range")
        print("4. Get Monthly report")
        print("5. Check the attendance of a student")
        print("6. Get the attendance details of a particular student")
        print("7. Send alert mails for students with lower percentages")
        print("8. Attendance trends chart")
        print("9. Get the details of the attendance in excel format")
        print("10. Exit Program")

        option = input("Select an option: ")

        if option == '1':
            course_id = get_course_id(cursor, current_date, current_time)
            if course_id:
                mark_all_absent(conn, cursor, course_id, current_date)
                print("Recording attendance, press 'q' to terminate")
                process = subprocess.Popen(['python', 'record_attendance.py'])
                choice = input()
                while choice != 'q':
                    print("You have to press 'q' to stop recording the attendance")
                    choice = input()
                process.terminate()
                print("Stopped recording")
                print_absentees(cursor, course_id, current_date)
            else:
                print("Unable to get a course id")
        elif option == '2':
            manual_attendance(cursor, conn)
        elif option == '3':
            check_attendance_range(cursor)
        elif option == '4':
            generate_monthly_attendance_report(cursor)
        elif option == '5':
            course_id = input("Enter the course id: ")
            date = input("Enter the date (YYYY-MM-DD): ")
            reg_no = input("Enter the student id: ")
            existing_record = is_existing_student(
                cursor, reg_no, course_id, date)
            if existing_record:
                print(existing_record[4])
            else:
                print("No record found")
        elif option == '6':
            check_particular_day_attendance(cursor)
        elif option == '7':
            send_mail(cursor)
        elif option == '8':
            plot_graph(cursor)
        elif option == '9':
            create_attendance_excel(cursor)
        elif option == '10':
            print("Quitting the program.")
            break

    conn.close()


if __name__ == "__main__":
    main()
