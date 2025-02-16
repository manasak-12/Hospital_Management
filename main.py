import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector as c
from ttkthemes import ThemedStyle

def on_enter(e):
    e.widget['background'] = '#0052cc'
    e.widget['foreground'] = 'white'

def on_leave(e):
    e.widget['background'] = 'SystemButtonFace'
    e.widget['foreground'] = 'black'



# Establish MySQL connection
conn = c.connect(
    host="localhost",
    user="root",
    passwd=""
)

if conn.is_connected():
    csr = conn.cursor()

    # Check if the database exists
    csr.execute("SHOW DATABASES like 'HospitalManagement'")
    database = csr.fetchone()
    if 'hospitalmanagement' not in database:
        csr.execute("CREATE DATABASE HospitalManagement")

    # Use the database
    csr.execute("USE HospitalManagement")

    # Create tables
    csr.execute("""
    CREATE TABLE IF NOT EXISTS DEPT (
        DepID INT PRIMARY KEY,
        D_NAME VARCHAR(50),
        FLOOR INT,
        TELEPHONE VARCHAR(15)
    )
    """)

    csr.execute("""
    CREATE TABLE IF NOT EXISTS DOCTOR (
        DID INT PRIMARY KEY,
        F_NAME VARCHAR(50),
        L_NAME VARCHAR(50),
        SPEC VARCHAR(50),
        PH VARCHAR(15)
    )
    """)

    csr.execute("""
    CREATE TABLE IF NOT EXISTS PATIENT (
        PID INT PRIMARY KEY,
        F_NAME VARCHAR(50),
        L_NAME VARCHAR(50),
        DOB DATE,
        PH VARCHAR(15)
    )
    """)

    csr.execute("""
    CREATE TABLE IF NOT EXISTS APPOINTMENT (
        AID INT PRIMARY KEY,
        PID INT,
        DID INT,
        A_DATE DATE,
        A_TIME TIME,
        DepID INT,
        FOREIGN KEY (PID) REFERENCES PATIENT(PID),
        FOREIGN KEY (DID) REFERENCES DOCTOR(DID),
        FOREIGN KEY (DepID) REFERENCES DEPT(DepID)
    )
    """)

    csr.execute("""
    CREATE TABLE IF NOT EXISTS MED_RECORD (
        RID INT PRIMARY KEY,
        PID INT,
        DID INT,
        LAST_VISIT DATE,
        DIAGNOSIS TEXT,
        FOREIGN KEY (PID) REFERENCES PATIENT(PID),
        FOREIGN KEY (DID) REFERENCES DOCTOR(DID)
    )
    """)

    conn.commit()

else:
    print("Failed to connect to MySQL")


# Tkinter GUI
root = tk.Tk()
root.title("Hospital Management System")
root.geometry("1900x1080")

# Apply a default theme
style = ThemedStyle(root)
style.set_theme("arc")

# Configure styles
style.configure("TButton", font=("Helvetica", 12), padding=10)
style.configure("TLabel", font=("Helvetica", 12), padding=5)


# root.tk.call("source", "azure.tcl")
# root.tk.call("set_theme", "dark")



# Function to close MySQL connection
def on_closing():
    csr.close()
    conn.close()
    root.destroy()

# Bind the closing event
root.protocol("WM_DELETE_WINDOW", on_closing)

# Tabs for different functionalities
tabControl = ttk.Notebook(root)
tab_patient = ttk.Frame(tabControl)
tab_doctor = ttk.Frame(tabControl)
tab_dept = ttk.Frame(tabControl)
tab_appointment = ttk.Frame(tabControl)
tab_med_record = ttk.Frame(tabControl)

tabControl.add(tab_patient, text='Patients')
tabControl.add(tab_doctor, text='Doctors')
tabControl.add(tab_dept, text='Departments')
tabControl.add(tab_appointment, text='Appointments')
tabControl.add(tab_med_record, text='Medical Records')
tabControl.pack(expand=0, fill="both")

# Patient Information
def add_patient():
    csr.execute("INSERT INTO PATIENT (PID, F_NAME, L_NAME, DOB, PH) VALUES (%s, %s, %s, %s, %s)",
                (entry_pid.get(), entry_fname.get(), entry_lname.get(), entry_dob.get(), entry_ph.get()))
    conn.commit()
    messagebox.showinfo("Success", "Patient added successfully")
    view_patients()

def view_patients():
    for row in tree_patient.get_children():
        tree_patient.delete(row)
    csr.execute("SELECT * FROM PATIENT")
    rows = csr.fetchall()
    for row in rows:
        tree_patient.insert("", tk.END, values=row)

def search_patient():
    for row in tree_patient.get_children():
        tree_patient.delete(row)
    query = f"SELECT * FROM PATIENT WHERE {search_field_patient.get()} LIKE %s"
    csr.execute(query, (f"%{search_entry_patient.get()}%",))
    rows = csr.fetchall()
    for row in rows:
        tree_patient.insert("", tk.END, values=row)

def update_patient():
    selected_item = tree_patient.selection()[0]
    pid = tree_patient.item(selected_item, 'values')[0]
    csr.execute("""
    UPDATE PATIENT 
    SET F_NAME=%s, L_NAME=%s, DOB=%s, PH=%s 
    WHERE PID=%s
    """, (entry_fname.get(), entry_lname.get(), entry_dob.get(), entry_ph.get(), pid))
    conn.commit()
    messagebox.showinfo("Success", "Patient updated successfully")
    view_patients()

def delete_patient():
    selected_item = tree_patient.selection()[0]
    pid = tree_patient.item(selected_item, 'values')[0]
    csr.execute("DELETE FROM PATIENT WHERE PID=%s", (pid,))
    conn.commit()
    tree_patient.delete(selected_item)
    messagebox.showinfo("Success", "Patient deleted successfully")

frame_patient = ttk.LabelFrame(tab_patient, text="Patient Information")
frame_patient.pack(fill="x", padx=10, pady=10)

# Adding search functionality
ttk.Label(frame_patient, text="Search:").grid(row=0, column=2, padx=5, pady=5)
search_field_patient = ttk.Combobox(frame_patient, values=["PID", "F_NAME", "L_NAME", "DOB", "PH"], width=10)
search_field_patient.grid(row=0, column=3, padx=5, pady=5)
search_entry_patient = ttk.Entry(frame_patient)
search_entry_patient.grid(row=1, column=3, padx=5, pady=5)
ttk.Button(frame_patient, text="Search", command=search_patient).grid(row=0, column=4, padx=5, pady=5)


ttk.Label(frame_patient, text="Patient ID:").grid(row=0, column=0, padx=5, pady=5)
entry_pid = ttk.Entry(frame_patient)
entry_pid.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_patient, text="First Name:").grid(row=1, column=0, padx=5, pady=5)
entry_fname = ttk.Entry(frame_patient)
entry_fname.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_patient, text="Last Name:").grid(row=2, column=0, padx=5, pady=5)
entry_lname = ttk.Entry(frame_patient)
entry_lname.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame_patient, text="Date of Birth:").grid(row=3, column=0, padx=5, pady=5)
entry_dob = ttk.Entry(frame_patient)
entry_dob.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(frame_patient, text="Phone:").grid(row=4, column=0, padx=5, pady=5)
entry_ph = ttk.Entry(frame_patient)
entry_ph.grid(row=4, column=1, padx=5, pady=5)

ttk.Button(frame_patient, text="Add Patient", command=add_patient).grid(row=5, column=0, pady=10)
ttk.Button(frame_patient, text="Update Patient", command=update_patient).grid(row=5, column=1, pady=10)
ttk.Button(frame_patient, text="Delete Patient", command=delete_patient).grid(row=5, column=2, pady=10)

tree_patient = ttk.Treeview(tab_patient, columns=("PID", "F_NAME", "L_NAME", "DOB", "PH"), show="headings")
tree_patient.heading("PID", text="Patient ID")
tree_patient.heading("F_NAME", text="First Name")
tree_patient.heading("L_NAME", text="Last Name")
tree_patient.heading("DOB", text="Date of Birth")
tree_patient.heading("PH", text="Phone")
tree_patient.pack(fill="both", expand=True)

ttk.Button(tab_patient, text="View Patients", command=view_patients).pack(pady=10)

# Doctor Information
def add_doctor():
    csr.execute("INSERT INTO DOCTOR (DID, F_NAME, L_NAME, SPEC, PH) VALUES (%s, %s, %s, %s, %s)",
                (entry_did.get(), entry_d_fname.get(), entry_d_lname.get(), entry_spec.get(), entry_d_ph.get()))
    conn.commit()
    messagebox.showinfo("Success", "Doctor added successfully")
    view_doctors()

def view_doctors():
    for row in tree_doctor.get_children():
        tree_doctor.delete(row)
    csr.execute("SELECT * FROM DOCTOR")
    rows = csr.fetchall()
    for row in rows:
        tree_doctor.insert("", tk.END, values=row)

def search_doctor():
    for row in tree_doctor.get_children():
        tree_doctor.delete(row)
    query = f"SELECT * FROM DOCTOR WHERE {search_field_doctor.get()} LIKE %s"
    csr.execute(query, (f"%{search_entry_doctor.get()}%",))
    rows = csr.fetchall()
    for row in rows:
        tree_doctor.insert("", tk.END, values=row)

def update_doctor():
    selected_item = tree_doctor.selection()[0]
    did = tree_doctor.item(selected_item, 'values')[0]
    csr.execute("""
    UPDATE DOCTOR 
    SET F_NAME=%s, L_NAME=%s, SPEC=%s, PH=%s 
    WHERE DID=%s
    """, (entry_d_fname.get(), entry_d_lname.get(), entry_spec.get(), entry_d_ph.get(), did))
    conn.commit()
    messagebox.showinfo("Success", "Doctor updated successfully")
    view_doctors()

def delete_doctor():
    selected_item = tree_doctor.selection()[0]
    did = tree_doctor.item(selected_item, 'values')[0]
    csr.execute("DELETE FROM DOCTOR WHERE DID=%s", (did,))
    conn.commit()
    tree_doctor.delete(selected_item)
    messagebox.showinfo("Success", "Doctor deleted successfully")

frame_doctor = ttk.LabelFrame(tab_doctor, text="Doctor Information")
frame_doctor.pack(fill="x", padx=10, pady=10)

# Adding search functionality
ttk.Label(frame_doctor, text="Search:").grid(row=0, column=2, padx=5, pady=5)
search_field_doctor = ttk.Combobox(frame_doctor, values=["DID", "F_NAME", "L_NAME", "SPEC", "PH"], width=10)
search_field_doctor.grid(row=0, column=3, padx=5, pady=5)
search_entry_doctor = ttk.Entry(frame_doctor)
search_entry_doctor.grid(row=1, column=3, padx=5, pady=5)
ttk.Button(frame_doctor, text="Search", command=search_doctor).grid(row=0, column=4, padx=5, pady=5)


ttk.Label(frame_doctor, text="Doctor ID:").grid(row=0, column=0, padx=5, pady=5)
entry_did = ttk.Entry(frame_doctor)
entry_did.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_doctor, text="First Name:").grid(row=1, column=0, padx=5, pady=5)
entry_d_fname = ttk.Entry(frame_doctor)
entry_d_fname.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_doctor, text="Last Name:").grid(row=2, column=0, padx=5, pady=5)
entry_d_lname = ttk.Entry(frame_doctor)
entry_d_lname.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame_doctor, text="Specialization:").grid(row=3, column=0, padx=5, pady=5)
entry_spec = ttk.Entry(frame_doctor)
entry_spec.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(frame_doctor, text="Phone:").grid(row=4, column=0, padx=5, pady=5)
entry_d_ph = ttk.Entry(frame_doctor)
entry_d_ph.grid(row=4, column=1, padx=5, pady=5)

ttk.Button(frame_doctor, text="Add Doctor", command=add_doctor).grid(row=5, column=0, pady=10)
ttk.Button(frame_doctor, text="Update Doctor", command=update_doctor).grid(row=5, column=1, pady=10)
ttk.Button(frame_doctor, text="Delete Doctor", command=delete_doctor).grid(row=5, column=2, pady=10)

tree_doctor = ttk.Treeview(tab_doctor, columns=("DID", "F_NAME", "L_NAME", "SPEC", "PH"), show="headings")
tree_doctor.heading("DID", text="Doctor ID")
tree_doctor.heading("F_NAME", text="First Name")
tree_doctor.heading("L_NAME", text="Last Name")
tree_doctor.heading("SPEC", text="Specialization")
tree_doctor.heading("PH", text="Phone")
tree_doctor.pack(fill="both", expand=True)

ttk.Button(tab_doctor, text="View Doctors", command=view_doctors).pack(pady=10)

# Department Information
def add_department():
    csr.execute("INSERT INTO DEPT (DepID, D_NAME, FLOOR, TELEPHONE) VALUES (%s, %s, %s, %s)",
                (entry_depid.get(), entry_dname.get(), entry_floor.get(), entry_telephone.get()))
    conn.commit()
    messagebox.showinfo("Success", "Department added successfully")
    view_departments()

def view_departments():
    for row in tree_dept.get_children():
        tree_dept.delete(row)
    csr.execute("SELECT * FROM DEPT")
    rows = csr.fetchall()
    for row in rows:
        tree_dept.insert("", tk.END, values=row)

def search_department():
    for row in tree_dept.get_children():
        tree_dept.delete(row)
    query = f"SELECT * FROM DEPT WHERE {search_field_dept.get()} LIKE %s"
    csr.execute(query, (f"%{search_entry_dept.get()}%",))
    rows = csr.fetchall()
    for row in rows:
        tree_dept.insert("", tk.END, values=row)
        
def update_department():
    selected_item = tree_dept.selection()[0]
    depid = tree_dept.item(selected_item, 'values')[0]
    csr.execute("""
    UPDATE DEPT 
    SET D_NAME=%s, FLOOR=%s, TELEPHONE=%s 
    WHERE DepID=%s
    """, (entry_dname.get(), entry_floor.get(), entry_telephone.get(), depid))
    conn.commit()
    messagebox.showinfo("Success", "Department updated successfully")
    view_departments()

def delete_department():
    selected_item = tree_dept.selection()[0]
    depid = tree_dept.item(selected_item, 'values')[0]
    csr.execute("DELETE FROM DEPT WHERE DepID=%s", (depid,))
    conn.commit()
    tree_dept.delete(selected_item)
    messagebox.showinfo("Success", "Department deleted successfully")

frame_dept = ttk.LabelFrame(tab_dept, text="Department Information")
frame_dept.pack(fill="x", padx=10, pady=10)

# Adding search functionality
ttk.Label(frame_dept, text="Search:").grid(row=0, column=2, padx=5, pady=5)
search_field_dept = ttk.Combobox(frame_dept, values=["DEPT_ID", "DEPT_NAME"], width=10)
search_field_dept.grid(row=0, column=3, padx=5, pady=5)
search_entry_dept = ttk.Entry(frame_dept)
search_entry_dept.grid(row=1, column=3, padx=5, pady=5)
ttk.Button(frame_dept, text="Search", command=search_department).grid(row=0, column=4, padx=5, pady=5)


ttk.Label(frame_dept, text="Department ID:").grid(row=0, column=0, padx=5, pady=5)
entry_depid = ttk.Entry(frame_dept)
entry_depid.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_dept, text="Name:").grid(row=1, column=0, padx=5, pady=5)
entry_dname = ttk.Entry(frame_dept)
entry_dname.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_dept, text="Floor:").grid(row=2, column=0, padx=5, pady=5)
entry_floor = ttk.Entry(frame_dept)
entry_floor.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame_dept, text="Telephone:").grid(row=3, column=0, padx=5, pady=5)
entry_telephone = ttk.Entry(frame_dept)
entry_telephone.grid(row=3, column=1, padx=5, pady=5)

ttk.Button(frame_dept, text="Add Department", command=add_department).grid(row=4, column=0, pady=10)
ttk.Button(frame_dept, text="Update Department", command=update_department).grid(row=4, column=1, pady=10)
ttk.Button(frame_dept, text="Delete Department", command=delete_department).grid(row=4, column=2, pady=10)

tree_dept = ttk.Treeview(tab_dept, columns=("DepID", "D_NAME", "FLOOR", "TELEPHONE"), show="headings")
tree_dept.heading("DepID", text="Department ID")
tree_dept.heading("D_NAME", text="Name")
tree_dept.heading("FLOOR", text="Floor")
tree_dept.heading("TELEPHONE", text="Telephone")
tree_dept.pack(fill="both", expand=True)

ttk.Button(tab_dept, text="View Departments", command=view_departments).pack(pady=10)

# Appointment Information
def add_appointment():
    csr.execute("INSERT INTO APPOINTMENT (AID, PID, DID, A_DATE, A_TIME, DepID) VALUES (%s, %s, %s, %s, %s, %s)",
                (entry_aid.get(), entry_ap_pid.get(), entry_ap_did.get(), entry_adate.get(), entry_atime.get(), entry_ap_depid.get()))
    conn.commit()
    messagebox.showinfo("Success", "Appointment added successfully")
    view_appointments()

# Appointment Information
def view_appointments():
    for row in tree_appointment.get_children():
        tree_appointment.delete(row)
    csr.execute("""
    SELECT A.AID, P.F_NAME AS PatientName, D.F_NAME AS DoctorName, A.A_DATE, A.A_TIME, DP.D_NAME AS DepartmentName 
    FROM APPOINTMENT A
    JOIN PATIENT P ON A.PID = P.PID
    JOIN DOCTOR D ON A.DID = D.DID
    JOIN DEPT DP ON A.DepID = DP.DepID
    """)
    rows = csr.fetchall()
    for row in rows:
        tree_appointment.insert("", tk.END, values=row)

def search_appointment():
    for row in tree_appointment.get_children():
        tree_appointment.delete(row)
    query = f"""
    SELECT A.AID, P.F_NAME AS PatientName, D.F_NAME AS DoctorName, A.A_DATE, A.A_TIME, DP.D_NAME AS DepartmentName 
    FROM APPOINTMENT A
    JOIN PATIENT P ON A.PID = P.PID
    JOIN DOCTOR D ON A.DID = D.DID
    JOIN DEPT DP ON A.DepID = DP.DepID
    WHERE {search_field_appointment.get()} LIKE %s
    """
    csr.execute(query, (f"%{search_entry_appointment.get()}%",))
    rows = csr.fetchall()
    for row in rows:
        tree_appointment.insert("", tk.END, values=row)

def update_appointment():
    selected_item = tree_appointment.selection()[0]
    aid = tree_appointment.item(selected_item, 'values')[0]
    csr.execute("""
    UPDATE APPOINTMENT 
    SET PID=%s, DID=%s, A_DATE=%s, A_TIME=%s, DepID=%s 
    WHERE AID=%s
    """, (entry_ap_pid.get(), entry_ap_did.get(), entry_adate.get(), entry_atime.get(), entry_ap_depid.get(), aid))
    conn.commit()
    messagebox.showinfo("Success", "Appointment updated successfully")
    view_appointments()

def delete_appointment():
    selected_item = tree_appointment.selection()[0]
    aid = tree_appointment.item(selected_item, 'values')[0]
    csr.execute("DELETE FROM APPOINTMENT WHERE AID=%s", (aid,))
    conn.commit()
    tree_appointment.delete(selected_item)
    messagebox.showinfo("Success", "Appointment deleted successfully")

frame_appointment = ttk.LabelFrame(tab_appointment, text="Appointment Information")
frame_appointment.pack(fill="x", padx=10, pady=10)

# Adding search functionality
ttk.Label(frame_appointment, text="Search:").grid(row=0, column=2, padx=5, pady=5)
search_field_appointment = ttk.Combobox(frame_appointment, values=["APPT_ID", "PATIENT_ID", "DOCTOR_ID", "DATE", "TIME"], width=10)
search_field_appointment.grid(row=0, column=3, padx=5, pady=5)
search_entry_appointment = ttk.Entry(frame_appointment)
search_entry_appointment.grid(row=1, column=3, padx=5, pady=5)
ttk.Button(frame_appointment, text="Search", command=search_appointment).grid(row=0, column=4, padx=5, pady=5)


ttk.Label(frame_appointment, text="Appointment ID:").grid(row=0, column=0, padx=5, pady=5)
entry_aid = ttk.Entry(frame_appointment)
entry_aid.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_appointment, text="Patient ID:").grid(row=1, column=0, padx=5, pady=5)
entry_ap_pid = ttk.Entry(frame_appointment)
entry_ap_pid.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_appointment, text="Doctor ID:").grid(row=2, column=0, padx=5, pady=5)
entry_ap_did = ttk.Entry(frame_appointment)
entry_ap_did.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame_appointment, text="Date:").grid(row=3, column=0, padx=5, pady=5)
entry_adate = ttk.Entry(frame_appointment)
entry_adate.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(frame_appointment, text="Time:").grid(row=4, column=0, padx=5, pady=5)
entry_atime = ttk.Entry(frame_appointment)
entry_atime.grid(row=4, column=1, padx=5, pady=5)

ttk.Label(frame_appointment, text="Department ID:").grid(row=5, column=0, padx=5, pady=5)
entry_ap_depid = ttk.Entry(frame_appointment)
entry_ap_depid.grid(row=5, column=1, padx=5, pady=5)

ttk.Button(frame_appointment, text="Add Appointment", command=add_appointment).grid(row=6, column=0, pady=10)
ttk.Button(frame_appointment, text="Update Appointment", command=update_appointment).grid(row=6, column=1, pady=10)
ttk.Button(frame_appointment, text="Delete Appointment", command=delete_appointment).grid(row=6, column=2, pady=10)

tree_appointment = ttk.Treeview(tab_appointment, columns=("AID", "PID", "DID", "A_DATE", "A_TIME", "DepID"), show="headings")
tree_appointment.heading("AID", text="Appointment ID")
tree_appointment.heading("PID", text="Patient ID")
tree_appointment.heading("DID", text="Doctor ID")
tree_appointment.heading("A_DATE", text="Date")
tree_appointment.heading("A_TIME", text="Time")
tree_appointment.heading("DepID", text="Department ID")
tree_appointment.pack(fill="both", expand=True)

ttk.Button(tab_appointment, text="View Appointments", command=view_appointments).pack(pady=10)

# Medical Records Information
def add_medical_record():
    csr.execute("INSERT INTO MED_RECORD (RID, PID, DID, LAST_VISIT, DIAGNOSIS) VALUES (%s, %s, %s, %s, %s)",
                (entry_rid.get(), entry_mr_pid.get(), entry_mr_did.get(), entry_last_visit.get(), entry_diagnosis.get()))
    conn.commit()
    messagebox.showinfo("Success", "Medical record added successfully")
    view_medical_records()

# Medical Records Information
def view_medical_records():
    for row in tree_med_record.get_children():
        tree_med_record.delete(row)
    csr.execute("""
    SELECT M.RID, P.F_NAME AS PatientName, D.F_NAME AS DoctorName, M.LAST_VISIT, M.DIAGNOSIS 
    FROM MED_RECORD M
    JOIN PATIENT P ON M.PID = P.PID
    JOIN DOCTOR D ON M.DID = D.DID
    """)
    rows = csr.fetchall()
    for row in rows:
        tree_med_record.insert("", tk.END, values=row)

def search_med_record():
    for row in tree_med_record.get_children():
        tree_med_record.delete(row)
    query = f"""
    SELECT M.RID, P.F_NAME AS PatientName, D.F_NAME AS DoctorName, M.LAST_VISIT, M.DIAGNOSIS 
    FROM MED_RECORD M
    JOIN PATIENT P ON M.PID = P.PID
    JOIN DOCTOR D ON M.DID = D.DID
    WHERE {search_field_med_record.get()} LIKE %s
    """
    csr.execute(query, (f"%{search_entry_med_record.get()}%",))
    rows = csr.fetchall()
    for row in rows:
        tree_med_record.insert("", tk.END, values=row)

def update_medical_record():
    selected_item = tree_med_record.selection()[0]
    rid = tree_med_record.item(selected_item, 'values')[0]
    csr.execute("""
    UPDATE MED_RECORD 
    SET PID=%s, DID=%s, LAST_VISIT=%s, DIAGNOSIS=%s 
    WHERE RID=%s
    """, (entry_mr_pid.get(), entry_mr_did.get(), entry_last_visit.get(), entry_diagnosis.get(), rid))
    conn.commit()
    messagebox.showinfo("Success", "Medical record updated successfully")
    view_medical_records()

def delete_medical_record():
    selected_item = tree_med_record.selection()[0]
    rid = tree_med_record.item(selected_item, 'values')[0]
    csr.execute("DELETE FROM MED_RECORD WHERE RID=%s", (rid,))
    conn.commit()
    tree_med_record.delete(selected_item)
    messagebox.showinfo("Success", "Medical record deleted successfully")

frame_med_record = ttk.LabelFrame(tab_med_record, text="Medical Record Information")
frame_med_record.pack(fill="x", padx=10, pady=10)

# Adding search functionality
ttk.Label(frame_med_record, text="Search:").grid(row=0, column=2, padx=5, pady=5)
search_field_med_record = ttk.Combobox(frame_med_record, values=["RECORD_ID", "PATIENT_ID", "DOCTOR_ID", "DATE", "NOTES"], width=10)
search_field_med_record.grid(row=0, column=3, padx=5, pady=5)
search_entry_med_record = ttk.Entry(frame_med_record)
search_entry_med_record.grid(row=1, column=3, padx=5, pady=5)
ttk.Button(frame_med_record, text="Search", command=search_med_record).grid(row=0, column=4, padx=5, pady=5)


ttk.Label(frame_med_record, text="Record ID:").grid(row=0, column=0, padx=5, pady=5)
entry_rid = ttk.Entry(frame_med_record)
entry_rid.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_med_record, text="Patient ID:").grid(row=1, column=0, padx=5, pady=5)
entry_mr_pid = ttk.Entry(frame_med_record)
entry_mr_pid.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_med_record, text="Doctor ID:").grid(row=2, column=0, padx=5, pady=5)
entry_mr_did = ttk.Entry(frame_med_record)
entry_mr_did.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame_med_record, text="Last Visit Date:").grid(row=3, column=0, padx=5, pady=5)
entry_last_visit = ttk.Entry(frame_med_record)
entry_last_visit.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(frame_med_record, text="Diagnosis:").grid(row=4, column=0, padx=5, pady=5)
entry_diagnosis = ttk.Entry(frame_med_record)
entry_diagnosis.grid(row=4, column=1, padx=5, pady=5)

ttk.Button(frame_med_record, text="Add Medical Record", command=add_medical_record).grid(row=5, column=0, pady=10)
ttk.Button(frame_med_record, text="Update Medical Record", command=update_medical_record).grid(row=5, column=1, pady=10)
ttk.Button(frame_med_record, text="Delete Medical Record", command=delete_medical_record).grid(row=5, column=2, pady=10)

tree_med_record = ttk.Treeview(tab_med_record, columns=("RID", "PatientName", "DoctorName", "LAST_VISIT", "DIAGNOSIS"), show="headings")
tree_med_record.heading("RID", text="Record ID")
tree_med_record.heading("PatientName", text="Patient Name")
tree_med_record.heading("DoctorName", text="Doctor Name")
tree_med_record.heading("LAST_VISIT", text="Last Visit Date")
tree_med_record.heading("DIAGNOSIS", text="Diagnosis")
tree_med_record.pack(fill="both", expand=True)


ttk.Button(tab_med_record, text="View Medical Records", command=view_medical_records).pack(pady=10)

root.mainloop()