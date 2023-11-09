import socket
import mysql.connector
from datetime import datetime

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Nani@01012004',
    'database': 'dbms_project',
}

UDP_IP = "0.0.0.0"
UDP_PORT = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("Connected to the database")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit()


def get_course_id(date, time):
    day_of_week = date.strftime('%A')
    fetch_course_id_query = "SELECT course_id FROM timetable WHERE day = %s AND %s BETWEEN start_time AND end_time"
    cursor.execute(fetch_course_id_query, (day_of_week, time))
    course_id_result = cursor.fetchone()
    if course_id_result:
        return course_id_result[0]
    else:
        return None


while True:
    data, addr = sock.recvfrom(1024)
    student_id = data.decode()
    student_id = student_id[:-1]
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    status = "present"
    course_id = get_course_id(date, time)
    try:
        cursor.execute("INSERT INTO attendance (student_id,course_id, date, time, status) VALUES (%s,%s, %s, %s, %s)",
                       (student_id, course_id, date, time, status))
        conn.commit()
        print("Recorded attendance for Student ID:", student_id)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
