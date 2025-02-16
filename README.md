# Hospital Management System

## Description
This is a **Hospital Management System** built using **Python (Tkinter)** for the GUI and **MySQL** as the database. The system allows users to manage patients, doctors, departments, appointments, and medical records efficiently.

## Features
- **MySQL Integration:** Connects to a MySQL database and automatically creates required tables if they do not exist.
- **Tabbed Interface:** Uses Tkinter's `Notebook` for navigation between Patients, Doctors, Departments, Appointments, and Medical Records.
- **CRUD Operations:**
  - Add, update, delete, and search records for each module.
  - Data is displayed in a `Treeview` table.
- **Themed UI:** Utilizes `ttkthemes` to enhance the look and feel of the application.

## Installation
### Prerequisites
Ensure you have the following installed:
- **Python 3.x**
- **MySQL Server**
- Required Python libraries:
  ```sh
  pip install mysql-connector-python tk ttkthemes
  ```

### Database Setup
1. Open MySQL and create a user with the necessary permissions (if not already created).
2. The script will automatically create a `HospitalManagement` database and necessary tables upon execution.

## Running the Application
1. Clone or download the project files.
2. Navigate to the project folder and run:
   ```sh
   python main.py
   ```
## Snapshots

![Image1]("C:\Users\Manasa\Pictures\Screenshots\Screenshot 2025-02-16 233303.png")  

## Usage
- **Patients Tab:** Add, search, update, and delete patient records.
- **Doctors Tab:** Manage doctor details and specializations.
- **Departments Tab:** Keep track of hospital departments.
- **Appointments Tab:** Schedule and manage appointments.
- **Medical Records Tab:** Store and retrieve medical records.

## Security Considerations
- Avoid hardcoding the MySQL password in the script; use environment variables.
- Add exception handling for database operations to prevent crashes.
- Validate user input to prevent SQL injection.

## Future Improvements
- Implement user authentication for access control.
- Add reporting and analytics features.
- Improve UI with advanced styling.



