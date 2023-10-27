import subprocess
import mysql.connector
from datetime import datetime

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
    print(day_of_week)
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
        print("4. Monthly report")
        print("5. Option 5")
        print("6. Option 6")
        print("7. Option 7")
        print("8. Option 8")
        print("9. Option 9")
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
        elif option == '10':
            print("Quitting the program.")
            break

    conn.close()


if __name__ == "__main__":
    main()
