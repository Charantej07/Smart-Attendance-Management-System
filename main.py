import subprocess
import mysql.connector
from datetime import datetime
import time


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'khya',
    'database': 'dbms_project',
}
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("Connected to the database")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit()

current_date = datetime.now().date()
current_time = datetime.now().time()
# current_time = datetime.strptime("11:45:00", "%H:%M:%S")

day_of_week = current_date.strftime('%A')
current_time_str = current_time.strftime('%H:%M:%S')
course_id = None


def mark_absent(student_id, course_id, current_date, current_time):
    check_query = "SELECT * FROM attendance WHERE student_id = %s AND course_id = %s AND date = %s"
    cursor.execute(check_query, (student_id, course_id, current_date))
    existing_entry = cursor.fetchone()

    if existing_entry:
        pass
    else:
        attendance_insert_query = "INSERT INTO attendance (student_id, course_id, date, time, status) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(attendance_insert_query, (student_id,
                       course_id, current_date, current_time, "absent"))
        conn.commit()


def marking_all_absent():
    global course_id
    fetch_course_id = "SELECT course_id FROM timetable WHERE day = %s AND %s BETWEEN start_time AND end_time"
    cursor.execute(fetch_course_id, (day_of_week, current_time_str))
    result = cursor.fetchone()
    if result:
        course_id = result[0]
    else:
        return False
    student_query = "SELECT student_id FROM student"
    cursor.execute(student_query)
    students = cursor.fetchall()

    for student in students:
        student_id = student[0]
        mark_absent(student_id, course_id, current_date, current_time)
    return True


def print_absenties():
    print_absenties_query = "SELECT student_id FROM attendance WHERE course_id = %s AND date = %s AND status = %s"
    cursor.execute(print_absenties_query, (course_id, current_date, "absent"))
    existing_entry = cursor.fetchall()
    print("Absenties list")
    for entry in existing_entry:
        print(entry[0])


while True:
    print("\nMenu Options:")
    print("1. Start Attendance Recording ")
    print("2. Option 2")
    print("3. Option 3")
    print("4. Option 4")
    print("5. Option 5")
    print("6. Option 6")
    print("7. Option 7")
    print("8. Option 8")
    print("9. Option 9")
    print("10. Exit Program")

    option = input("Select an option: ")

    if option == '1':
        received_course_id = marking_all_absent()
        if (not received_course_id):
            print("Course ID not found for the current date and time.")
            time.sleep(2)
            continue
        else:
            print("Recording attendance, press q to terminate")
            process = subprocess.Popen(['python', 'test2.py'])
            ch = input()
            while ch != 'q':
                print("You have to press q to stop recording the attendance")
                ch = input()
            process.terminate()
            print("Stopped recording")
            print_absenties()

    elif option == '2':
        course_id = input("Enter course id: ")
        date = input(
            'Enter the date on which attendance has to be modified (YYYY-MM-DD): ')
        student_id = input("Enter the roll number of the student: ")
        get_status_query = " select status from attendance where student_id = %s and course_id = %s and date = %s;"
        cursor.execute(get_status_query, (student_id, course_id, date))
        status = cursor.fetchall()

        print(student_id, "\t", status[0][0])
        print("Enter P to mark as present \ A to mark as absent: ")

        update_attendance_query = "Update attendance set status = %s where student_id = %s and course_id = %s and date = %s;"
        cha = 'x'
        valid_cha = ['p', 'P', 'a', 'A']
        while (cha not in valid_cha):
            cha = input()
            if (cha == 'P' or cha == 'p'):
                status = 'present'
            elif (cha == 'A' or cha == 'a'):
                status = 'absent'
            else:
                print("Enter valid input")
        cursor.execute(update_attendance_query,
                       (status, student_id, course_id, date))
        print("Attendance modified successfully!")
        cursor.execute(get_status_query, (student_id, course_id, date))
        status = cursor.fetchall()

        print(student_id, "\t", status[0][0])
        conn.commit()
        pass
    elif option == '3':
        pass
    elif option == '4':
        pass
    elif option == '5':
        pass
    elif option == '6':
        pass
    elif option == '7':
        pass
    elif option == '8':
        pass
    elif option == '9':
        pass
    elif option == '10':
        print("Quitting the program.")
        break

conn.close()
