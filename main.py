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
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("Connected to the database")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit()

# Main menu loop
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
    print("10. Option 10")
    print("0. Exit Program")

    option = input("Select an option: ")

    if option == '0':
        print("Exiting the program.")
        break
    elif option == '1':
        # Start attendance recording (similar to your previous loop)
        print("Recording attendance, press q to terminate")
        process = subprocess.Popen(['python', 'record_attendance.py'])
        ch = input()
        while ch != 'q':
            print("You have to press q to stop recording the attendance")
            ch = input()
        process.terminate()
        print("Stopped recording")
    elif option == '2':
        # Option 2 code
        pass
    elif option == '3':
        # Option 3 code
        pass
    # Add code for the other menu options (2-10)

# Close the database connection
conn.close()
