# Smart Attendance Management System

📚 Welcome to the Smart Attendance Management System, a sophisticated solution designed to streamline attendance tracking and management using RFID technology, a Flask-based web interface, and a MySQL database.

rushita..

## Overview

This project offers an integrated system that encompasses multiple components:

### 1. RFID Card Reader (Arduino Sketch)

- `Scanning_ID_Card.ino`: The heart of the physical setup. It operates an ESP8266-based RFID card reader.
- **Functionality**: This module reads student IDs using RFID cards and communicates this data via UDP to the central server.

### 2. Flask Application (Attendance Management)

- `app.py`: The core of the web-based application, built using Flask.
- **Features**:
  - Attendance Recording: Allows real-time recording of student attendance.
  - Email Notifications: Automated email alerts to students based on attendance thresholds.
  - Reporting and Analysis: Offers insights into attendance trends and statistics.
- **Integration**: Seamlessly communicates with a MySQL database to manage attendance records.

### 3. Attendance Recording Script

- `record_attendance.py`: Listens for incoming UDP messages from the RFID reader.
- **Functionality**: Processes student ID data received via UDP, marks their attendance in the MySQL database, ensuring a robust and real-time attendance tracking mechanism.

## Functionality Highlights

🌟 **RFID Card Reader**:
- Effortlessly captures student IDs using RFID cards for swift identification.
- Sends acquired data to the Flask application for centralized attendance management.

🚀 **Flask Application**:
- Empowers users to record attendance efficiently.
- Automated email notifications for students falling below attendance thresholds.
- Comprehensive reporting and analytical capabilities for informed decision-making.

🔧 **Attendance Recording Script**:
- Dedicated script to handle real-time attendance updates based on incoming RFID data.

## Project Structure

📁 The project structure comprises:
- Source code for RFID communication (`Scanning_ID_Card.ino`) in the folder Scanning_ID_Card
- Flask-based web application (`app.py`)
- Script for real-time attendance updates (`record_attendance.py`)
- Organized the HTML files in the template folder and CSS and JS files in the static folder.
- Provided the ER Diagram of the Database.

## Setup and Usage

🔧 Getting started with the Smart Attendance Management System:

1. **RFID Configuration**:
   - Set up the RFID card reader according to the specifications outlined in `Scanning_ID_Card.ino`.

2. **Flask Application**:
   - Launch the Flask-based application using `app.py`.
   - Ensure MySQL is configured with the necessary database schema and connection details.

3. **Attendance Recording**:
   - Run the attendance recording script `record_attendance.py` to listen for incoming RFID data and update attendance records.

4. **Interface Interaction**:
   - Access the Flask web interface to utilize various attendance functionalities.

## Additional Information

📝 This project is an ongoing endeavor, constantly evolving to incorporate advanced features and optimizations. 

🔗 Contributions, suggestions, and feedback from the community are highly encouraged and welcomed.

## Contributors

👨‍💻 Meet the brilliant minds behind this project:
- [Sai Charan Teja](https://github.com/Charantej07)
- [Khyathi Devi](https://github.com/khyatae)
- [Rushita](https://github.com/rushitagandham)

## License

📜 This project is licensed under the MIT License.

