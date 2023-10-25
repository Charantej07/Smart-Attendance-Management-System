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

while True:
    data, addr = sock.recvfrom(1024)
    student_id = data.decode()
    print("Received Student ID:", student_id)
    student_id = student_id[:-1]

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    status = "Present"

    try:
        cursor.execute("INSERT INTO attendance (student_id, date, time, status) VALUES (%s, %s, %s, %s)",
                       (student_id, date, time, status))
        conn.commit()
        print("Inserted into the database")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


conn.close()
