import tkinter as tk
from tkinter import ttk, messagebox, font
import mysql.connector as c
import re
from datetime import datetime
from PIL import Image, ImageTk
import os

# Modern Color Scheme
class ModernColors:
    PRIMARY = "#2563eb"        # Blue
    PRIMARY_DARK = "#1d4ed8"   # Dark Blue
    SECONDARY = "#10b981"      # Green
    ACCENT = "#f59e0b"         # Orange
    BACKGROUND = "#f8fafc"     # Light Gray
    SURFACE = "#ffffff"        # White
    TEXT_PRIMARY = "#1f2937"   # Dark Gray
    TEXT_SECONDARY = "#6b7280" # Medium Gray
    SUCCESS = "#059669"        # Success Green
    ERROR = "#dc2626"          # Error Red
    WARNING = "#d97706"        # Warning Orange

# Validation Functions
class ValidationUtils:
    @staticmethod
    def validate_phone(phone):
        phone = re.sub(r'[\s-]', '', phone)
        if re.match(r'^\d{10}$', phone):
            return True, phone
        elif re.match(r'^(\+91|91)?\d{10}$', phone):
            return True, phone
        else:
            return False, "Phone number must be 10 digits (e.g., 9876543210 or +91-9876543210)"
    
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, email
        else:
            return False, "Invalid email format (e.g., user@example.com)"
    
    @staticmethod
    def validate_date(date_str):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, date_str
        except ValueError:
            return False, "Date must be in YYYY-MM-DD format (e.g., 2024-12-31)"
    
    @staticmethod
    def validate_time(time_str):
        try:
            datetime.strptime(time_str, '%H:%M')
            return True, time_str
        except ValueError:
            return False, "Time must be in HH:MM format (e.g., 14:30)"
    
    @staticmethod
    def validate_id(id_str, field_name):
        try:
            id_val = int(id_str)
            if id_val > 0:
                return True, str(id_val)
            else:
                return False, f"{field_name} must be a positive number"
        except ValueError:
            return False, f"{field_name} must be a valid number"
    
    @staticmethod
    def validate_name(name):
        if re.match(r'^[a-zA-Z\s]+$', name) and len(name.strip()) > 0:
            return True, name.strip()
        else:
            return False, "Name must contain only letters and spaces"
    
    @staticmethod
    def validate_not_empty(value, field_name):
        if value.strip():
            return True, value.strip()
        else:
            return False, f"{field_name} cannot be empty"

# Enhanced Entry Widget with Modern Styling
class ModernEntry(tk.Entry):
    def __init__(self, parent, validation_func=None, placeholder="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.validation_func = validation_func
        self.placeholder = placeholder
        self.placeholder_color = ModernColors.TEXT_SECONDARY
        self.normal_color = ModernColors.TEXT_PRIMARY
        
        # Configure styling
        self.configure(
            font=("Segoe UI", 10),
            bg=ModernColors.SURFACE,
            fg=self.normal_color,
            relief="flat",
            bd=2,
            highlightthickness=2,
            highlightcolor=ModernColors.PRIMARY,
            highlightbackground="#e5e7eb"
        )
        
        # Placeholder functionality
        if placeholder:
            self.insert(0, placeholder)
            self.configure(fg=self.placeholder_color)
            self.bind('<FocusIn>', self.on_focus_in)
            self.bind('<FocusOut>', self.on_focus_out)
        
        # Validation binding
        if validation_func:
            self.bind('<KeyRelease>', self.on_key_release)
            self.bind('<FocusOut>', self.validate_field)
    
    def on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(fg=self.normal_color)
    
    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(fg=self.placeholder_color)
    
    def on_key_release(self, event):
        if self.validation_func and self.get() and self.get() != self.placeholder:
            is_valid, _ = self.validation_func(self.get())
            if not is_valid:
                self.configure(highlightbackground=ModernColors.ERROR, highlightcolor=ModernColors.ERROR)
            else:
                self.configure(highlightbackground="#e5e7eb", highlightcolor=ModernColors.PRIMARY)
    
    def validate_field(self, event):
        if self.validation_func and self.get() and self.get() != self.placeholder:
            is_valid, message = self.validation_func(self.get())
            if not is_valid:
                messagebox.showerror("Validation Error", message)
                self.focus_set()
    
    def get_value(self):
        """Get value, excluding placeholder text"""
        value = self.get()
        return "" if value == self.placeholder else value

# Modern Button Class
class ModernButton(tk.Button):
    def __init__(self, parent, text, command, style="primary", *args, **kwargs):
        super().__init__(parent, text=text, command=command, *args, **kwargs)
        
        # Style configurations
        styles = {
            "primary": {
                "bg": ModernColors.PRIMARY,
                "fg": "white",
                "activebackground": ModernColors.PRIMARY_DARK,
                "activeforeground": "white"
            },
            "secondary": {
                "bg": ModernColors.SECONDARY,
                "fg": "white",
                "activebackground": "#059669",
                "activeforeground": "white"
            },
            "danger": {
                "bg": ModernColors.ERROR,
                "fg": "white",
                "activebackground": "#b91c1c",
                "activeforeground": "white"
            },
            "warning": {
                "bg": ModernColors.WARNING,
                "fg": "white",
                "activebackground": "#b45309",
                "activeforeground": "white"
            }
        }
        
        style_config = styles.get(style, styles["primary"])
        
        self.configure(
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            pady=8,
            padx=16,
            cursor="hand2",
            **style_config
        )
        
        # Hover effects
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        self.configure(bg=self["activebackground"])
    
    def on_leave(self, e):
        self.configure(bg=self["bg"])

# Database connection
try:
    conn = c.connect(
        host="localhost",
        user="root",
        passwd="ENTER_PASSWORD"
    )
    
    if conn.is_connected():
        csr = conn.cursor()
        
        # Create database if not exists
        csr.execute("CREATE DATABASE IF NOT EXISTS HospitalManagement")
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
            PH VARCHAR(15),
            EMAIL VARCHAR(100)
        )
        """)

        csr.execute("""
        CREATE TABLE IF NOT EXISTS PATIENT (
            PID INT PRIMARY KEY,
            F_NAME VARCHAR(50),
            L_NAME VARCHAR(50),
            DOB DATE,
            PH VARCHAR(15),
            EMAIL VARCHAR(100)
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
        raise Exception("Failed to connect to MySQL")

except Exception as e:
    messagebox.showerror("Database Error", f"Error connecting to database: {str(e)}")

# Main Application Class
class ModernHospitalManagement:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_styles()
        self.create_header()
        self.create_navigation()
        self.create_main_content()
        self.setup_data()
        
        # Start the Tkinter event loop
        self.root.mainloop()

    def setup_window(self):
        self.root.title("Hospital Management System")
        self.root.geometry("1400x900")
        self.root.configure(bg=ModernColors.BACKGROUND)
        self.root.state('zoomed')  # Maximize window on Windows
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_styles(self):
        # Create custom fonts
        self.title_font = font.Font(family="Segoe UI", size=24, weight="bold")
        self.heading_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.subheading_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.body_font = font.Font(family="Segoe UI", size=10)
    
    def create_header(self):
        # Header frame
        header_frame = tk.Frame(self.root, bg=ModernColors.PRIMARY, height=80)
        header_frame.pack(fill="x", pady=(0, 2))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="🏥 Hospital Management System",
            font=self.title_font,
            bg=ModernColors.PRIMARY,
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Advanced Healthcare Management Solution",
            font=("Segoe UI", 10),
            bg=ModernColors.PRIMARY,
            fg="#93c5fd"
        )
        subtitle_label.pack()
    
    def create_navigation(self):
        # Navigation frame
        nav_frame = tk.Frame(self.root, bg=ModernColors.SURFACE, height=60)
        nav_frame.pack(fill="x", pady=(0, 10))
        nav_frame.pack_propagate(False)
        
        # Navigation buttons
        nav_buttons = [
            ("👥 Patients", self.show_patients),
            ("👨‍⚕️ Doctors", self.show_doctors),
            ("🏢 Departments", self.show_departments),
            ("📅 Appointments", self.show_appointments),
            ("📋 Medical Records", self.show_medical_records)
        ]
        
        button_frame = tk.Frame(nav_frame, bg=ModernColors.SURFACE)
        button_frame.pack(expand=True)
        
        self.nav_buttons = []
        for i, (text, command) in enumerate(nav_buttons):
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=("Segoe UI", 11, "bold"),
                bg=ModernColors.BACKGROUND,
                fg=ModernColors.TEXT_PRIMARY,
                relief="flat",
                bd=0,
                pady=12,
                padx=20,
                cursor="hand2"
            )
            btn.pack(side="left", padx=2)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=ModernColors.PRIMARY, fg="white"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY))
            self.nav_buttons.append(btn)
    
    def create_main_content(self):
        # Main content frame
        self.main_frame = tk.Frame(self.root, bg=ModernColors.BACKGROUND)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Default view - Dashboard
        self.show_dashboard()
    
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def highlight_nav_button(self, index):
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.configure(bg=ModernColors.PRIMARY, fg="white")
            else:
                btn.configure(bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY)
    
    def setup_data(self):
        # This can be used for initial data loading or setup
        pass

    def show_dashboard(self):
        self.clear_main_frame()
        
        dashboard_frame = tk.Frame(self.main_frame, bg=ModernColors.BACKGROUND)
        dashboard_frame.pack(fill="both", expand=True)
        
        # Welcome message
        welcome_label = tk.Label(
            dashboard_frame,
            text="Welcome to Hospital Management System",
            font=self.heading_font,
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        welcome_label.pack(pady=20)
        
        # Stats cards
        stats_frame = tk.Frame(dashboard_frame, bg=ModernColors.BACKGROUND)
        stats_frame.pack(pady=20)
        
        # Fetch actual data from the database
        try:
            csr.execute("SELECT COUNT(*) FROM PATIENT")
            patient_count = csr.fetchone()[0]
            
            csr.execute("SELECT COUNT(*) FROM DOCTOR")
            doctor_count = csr.fetchone()[0]
            
            today = datetime.now().strftime('%Y-%m-%d')
            csr.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE A_DATE = %s", (today,))
            appointment_count = csr.fetchone()[0]
            
            csr.execute("SELECT COUNT(*) FROM DEPT")
            department_count = csr.fetchone()[0]
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch dashboard stats: {str(e)}")
            patient_count = 0
            doctor_count = 0
            appointment_count = 0
            department_count = 0

        stats = [
            ("Total Patients", f"{patient_count}", ModernColors.PRIMARY),
            ("Total Doctors", f"{doctor_count}", ModernColors.SECONDARY),
            ("Appointments Today", f"{appointment_count}", ModernColors.WARNING),
            ("Departments", f"{department_count}", ModernColors.ERROR)
        ]
        
        for i, (title, count, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
            card.pack(side="left", padx=10, pady=10, ipadx=20, ipady=15)
            
            count_label = tk.Label(
                card,
                text=count,
                font=("Segoe UI", 24, "bold"),
                bg=ModernColors.SURFACE,
                fg=color
            )
            count_label.pack()
            
            title_label = tk.Label(
                card,
                text=title,
                font=("Segoe UI", 10),
                bg=ModernColors.SURFACE,
                fg=ModernColors.TEXT_SECONDARY
            )
            title_label.pack()

    def show_patients(self):
        self.clear_main_frame()
        self.highlight_nav_button(0)
        
        # Patient management frame
        patient_frame = tk.Frame(self.main_frame, bg=ModernColors.BACKGROUND)
        patient_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(
            patient_frame,
            text="👥 Patient Management",
            font=self.heading_font,
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        title_label.pack(pady=(0, 10))
        
        # Form section
        form_frame = tk.Frame(patient_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # MODIFIED: Reduced ipady and pady to make form section smaller.
        form_frame.pack(fill="x", pady=(0, 10), padx=20, ipady=10) 
        
        form_title = tk.Label(
            form_frame,
            text="Add/Update Patient",
            font=self.subheading_font,
            bg=ModernColors.SURFACE,
            fg=ModernColors.TEXT_PRIMARY
        )
        form_title.pack(pady=(5, 10))
        
        # Form fields in grid
        fields_frame = tk.Frame(form_frame, bg=ModernColors.SURFACE)
        fields_frame.pack(padx=40)
        
        # Create form fields
        self.create_patient_form(fields_frame)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=ModernColors.SURFACE)
        button_frame.pack(pady=10)
        
        ModernButton(button_frame, "Add Patient", self.add_patient, "primary").pack(side="left", padx=5)
        ModernButton(button_frame, "Update Patient", self.update_patient, "secondary").pack(side="left", padx=5)
        ModernButton(button_frame, "Delete Patient", self.delete_patient, "danger").pack(side="left", padx=5)
        ModernButton(button_frame, "Clear Form", self.clear_patient_form, "warning").pack(side="left", padx=5)
        
        # Search section
        search_frame = tk.Frame(patient_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # MODIFIED: Reduced ipady and pady to make search section smaller.
        search_frame.pack(fill="x", pady=(0, 10), padx=20, ipady=5) 
        
        search_title = tk.Label(
            search_frame,
            text="Search Patients",
            font=self.subheading_font,
            bg=ModernColors.SURFACE,
            fg=ModernColors.TEXT_PRIMARY
        )
        search_title.pack()
        
        search_controls = tk.Frame(search_frame, bg=ModernColors.SURFACE)
        search_controls.pack(pady=5)
        
        self.search_field_patient = ttk.Combobox(
            search_controls, 
            values=["PID", "F_NAME", "L_NAME", "PH", "EMAIL"],
            font=self.body_font,
            width=15
        )
        self.search_field_patient.pack(side="left", padx=5)
        self.search_field_patient.set("F_NAME")
        
        self.search_entry_patient = ModernEntry(
            search_controls,
            placeholder="Search...",
            width=25
        )
        self.search_entry_patient.pack(side="left", padx=5)
        
        ModernButton(search_controls, "Search", self.search_patient, "primary").pack(side="left", padx=5)
        ModernButton(search_controls, "View All", self.view_patients, "secondary").pack(side="left", padx=5)
        
        # Table section
        table_frame = tk.Frame(patient_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # The table now has more vertical space to expand into.
        table_frame.pack(fill="both", expand=True, padx=20)
        
        # Create treeview
        self.create_patient_table(table_frame)
        
        # Load initial data
        self.view_patients()
    
    def create_patient_form(self, parent):
        # Create form fields with modern styling
        fields = [
            ("Patient ID:", "entry_pid", lambda x: ValidationUtils.validate_id(x, "Patient ID")),
            ("First Name:", "entry_fname", ValidationUtils.validate_name),
            ("Last Name:", "entry_lname", ValidationUtils.validate_name),
            ("Date of Birth (YYYY-MM-DD):", "entry_dob", ValidationUtils.validate_date),
            ("Phone:", "entry_ph", ValidationUtils.validate_phone),
            ("Email:", "entry_email", ValidationUtils.validate_email)
        ]
        
        for i, (label_text, entry_name, validation_func) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            
            # Label
            label = tk.Label(
                parent,
                text=label_text,
                font=self.body_font,
                bg=ModernColors.SURFACE,
                fg=ModernColors.TEXT_PRIMARY
            )
            label.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            
            # Entry
            entry = ModernEntry(
                parent,
                validation_func=validation_func,
                width=25
            )
            entry.grid(row=row, column=col+1, padx=10, pady=5)
            setattr(self, entry_name, entry)
    
    def create_patient_table(self, parent):
        # Table title
        table_title = tk.Label(
            parent,
            text="Patient Records",
            font=self.subheading_font,
            bg=ModernColors.SURFACE,
            fg=ModernColors.TEXT_PRIMARY
        )
        table_title.pack(pady=(15, 10))
        
        # Create treeview with scrollbars
        tree_frame = tk.Frame(parent, bg=ModernColors.SURFACE)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        self.tree_patient = ttk.Treeview(
            tree_frame,
            columns=("PID", "F_NAME", "L_NAME", "DOB", "PH", "EMAIL"),
            show="headings",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Configure scrollbars
        v_scrollbar.configure(command=self.tree_patient.yview)
        h_scrollbar.configure(command=self.tree_patient.xview)
        
        # Headings
        headings = [
            ("PID", "Patient ID", 100),
            ("F_NAME", "First Name", 120),
            ("L_NAME", "Last Name", 120),
            ("DOB", "Date of Birth", 120),
            ("PH", "Phone", 120),
            ("EMAIL", "Email", 200)
        ]
        
        for col, heading, width in headings:
            self.tree_patient.heading(col, text=heading)
            self.tree_patient.column(col, width=width, minwidth=80)
        
        # Pack everything
        self.tree_patient.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind selection event
        self.tree_patient.bind('<<TreeviewSelect>>', self.on_patient_select)
    
    def on_patient_select(self, event):
        """Fill form when patient is selected"""
        if self.tree_patient.selection():
            item = self.tree_patient.selection()[0]
            values = self.tree_patient.item(item, 'values')
            
            # Clear and fill form
            entries = [self.entry_pid, self.entry_fname, self.entry_lname, 
                      self.entry_dob, self.entry_ph, self.entry_email]
            
            for i, entry in enumerate(entries):
                entry.delete(0, tk.END)
                if i < len(values):
                    entry.insert(0, values[i])
    
    def validate_patient_data(self):
        """Validate all patient form data"""
        errors = []
        
        validators = [
            (self.entry_pid.get_value(), lambda x: ValidationUtils.validate_id(x, "Patient ID")),
            (self.entry_fname.get_value(), ValidationUtils.validate_name),
            (self.entry_lname.get_value(), ValidationUtils.validate_name),
            (self.entry_dob.get_value(), ValidationUtils.validate_date),
            (self.entry_ph.get_value(), ValidationUtils.validate_phone),
        ]
        
        field_names = ["Patient ID", "First Name", "Last Name", "Date of Birth", "Phone"]
        
        for i, (value, validator) in enumerate(validators):
            if not value:
                errors.append(f"{field_names[i]} is required")
            else:
                is_valid, message = validator(value)
                if not is_valid:
                    errors.append(f"{field_names[i]}: {message}")
        
        # Email validation (optional)
        email_value = self.entry_email.get_value()
        if email_value:
            is_valid, message = ValidationUtils.validate_email(email_value)
            if not is_valid:
                errors.append(f"Email: {message}")
        
        return errors
    
    def add_patient(self):
        errors = self.validate_patient_data()
        if errors:
            messagebox.showerror("Validation Errors", "\n".join(errors))
            return
        
        try:
            # Check for duplicate Patient ID
            csr.execute("SELECT COUNT(*) FROM PATIENT WHERE PID = %s", (self.entry_pid.get_value(),))
            if csr.fetchone()[0] > 0:
                messagebox.showerror("Error", "Patient ID already exists!")
                return
            
            # Clean phone number
            _, clean_phone = ValidationUtils.validate_phone(self.entry_ph.get_value())
            
            csr.execute(
                "INSERT INTO PATIENT (PID, F_NAME, L_NAME, DOB, PH, EMAIL) VALUES (%s, %s, %s, %s, %s, %s)",
                (self.entry_pid.get_value(), self.entry_fname.get_value(), self.entry_lname.get_value(),
                 self.entry_dob.get_value(), clean_phone, self.entry_email.get_value())
            )
            conn.commit()
            messagebox.showinfo("Success", "Patient added successfully!")
            self.clear_patient_form()
            self.view_patients()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error adding patient: {str(e)}")
    
    def update_patient(self):
        if not self.tree_patient.selection():
            messagebox.showerror("Error", "Please select a patient to update")
            return
        
        errors = self.validate_patient_data()
        if errors:
            messagebox.showerror("Validation Errors", "\n".join(errors))
            return
        
        try:
            selected_item = self.tree_patient.selection()[0]
            old_pid = self.tree_patient.item(selected_item, 'values')[0]
            
            # Clean phone number
            _, clean_phone = ValidationUtils.validate_phone(self.entry_ph.get_value())
            
            csr.execute("""
            UPDATE PATIENT 
            SET PID=%s, F_NAME=%s, L_NAME=%s, DOB=%s, PH=%s, EMAIL=%s 
            WHERE PID=%s
            """, (self.entry_pid.get_value(), self.entry_fname.get_value(), self.entry_lname.get_value(),
                  self.entry_dob.get_value(), clean_phone, self.entry_email.get_value(), old_pid))
            conn.commit()
            messagebox.showinfo("Success", "Patient updated successfully!")
            self.view_patients()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error updating patient: {str(e)}")
    
    def delete_patient(self):
        if not self.tree_patient.selection():
            messagebox.showerror("Error", "Please select a patient to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient?"):
            try:
                selected_item = self.tree_patient.selection()[0]
                pid = self.tree_patient.item(selected_item, 'values')[0]
                csr.execute("DELETE FROM PATIENT WHERE PID=%s", (pid,))
                conn.commit()
                self.tree_patient.delete(selected_item)
                messagebox.showinfo("Success", "Patient deleted successfully!")
                self.clear_patient_form()
            except Exception as e:
                messagebox.showerror("Database Error", f"Error deleting patient: {str(e)}")
    
    def clear_patient_form(self):
        """Clear all patient form fields"""
        entries = [self.entry_pid, self.entry_fname, self.entry_lname, 
                  self.entry_dob, self.entry_ph, self.entry_email]
        for entry in entries:
            entry.delete(0, tk.END)
    
    def view_patients(self):
        """Load and display all patients"""
        try:
            for row in self.tree_patient.get_children():
                self.tree_patient.delete(row)
            
            csr.execute("SELECT * FROM PATIENT")
            rows = csr.fetchall()
            for row in rows:
                self.tree_patient.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading patients: {str(e)}")
    
    def search_patient(self):
        """Search patients based on field and value"""
        try:
            for row in self.tree_patient.get_children():
                self.tree_patient.delete(row)
            
            search_field = self.search_field_patient.get()
            search_value = self.search_entry_patient.get_value()
            
            if not search_field or not search_value:
                messagebox.showerror("Error", "Please select search field and enter search value")
                return
            
            query = f"SELECT * FROM PATIENT WHERE {search_field} LIKE %s"
            # Use parameterized query to prevent SQL injection
            csr.execute(query, (f"%{search_value}%",))
            rows = csr.fetchall()
            for row in rows:
                self.tree_patient.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Database Error", f"Error searching patients: {str(e)}")

    # ------------------ DOCTOR MANAGEMENT ------------------
    def show_doctors(self):
        self.clear_main_frame()
        self.highlight_nav_button(1)
        
        doctor_frame = tk.Frame(self.main_frame, bg=ModernColors.BACKGROUND)
        doctor_frame.pack(fill="both", expand=True)
        
        tk.Label(
            doctor_frame,
            text="👨‍⚕️ Doctor Management",
            font=self.heading_font,
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(pady=(0, 10))
        
        # Form section
        form_frame = tk.Frame(doctor_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # MODIFIED: Reduced ipady and pady to make form section smaller.
        form_frame.pack(fill="x", pady=(0, 10), padx=20, ipady=10) 
        
        tk.Label(form_frame, text="Add/Update Doctor", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack(pady=(5, 10))
        
        fields_frame = tk.Frame(form_frame, bg=ModernColors.SURFACE)
        fields_frame.pack(padx=40)
        self.create_doctor_form(fields_frame)
        
        button_frame = tk.Frame(form_frame, bg=ModernColors.SURFACE)
        button_frame.pack(pady=10)
        
        ModernButton(button_frame, "Add Doctor", self.add_doctor, "primary").pack(side="left", padx=5)
        ModernButton(button_frame, "Update Doctor", self.update_doctor, "secondary").pack(side="left", padx=5)
        ModernButton(button_frame, "Delete Doctor", self.delete_doctor, "danger").pack(side="left", padx=5)
        ModernButton(button_frame, "Clear Form", self.clear_doctor_form, "warning").pack(side="left", padx=5)

        # Search section
        search_frame = tk.Frame(doctor_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # MODIFIED: Reduced ipady and pady to make search section smaller.
        search_frame.pack(fill="x", pady=(0, 10), padx=20, ipady=5) 
        
        tk.Label(search_frame, text="Search Doctors", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack()
        
        search_controls = tk.Frame(search_frame, bg=ModernColors.SURFACE)
        search_controls.pack(pady=5)
        
        self.search_field_doctor = ttk.Combobox(search_controls, values=["DID", "F_NAME", "L_NAME", "SPEC", "PH", "EMAIL"], font=self.body_font, width=15)
        self.search_field_doctor.pack(side="left", padx=5)
        self.search_field_doctor.set("F_NAME")
        
        self.search_entry_doctor = ModernEntry(search_controls, placeholder="Search...", width=25)
        self.search_entry_doctor.pack(side="left", padx=5)
        
        ModernButton(search_controls, "Search", self.search_doctor, "primary").pack(side="left", padx=5)
        ModernButton(search_controls, "View All", self.view_doctors, "secondary").pack(side="left", padx=5)
        
        # Table section
        table_frame = tk.Frame(doctor_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # The table now has more vertical space to expand into.
        table_frame.pack(fill="both", expand=True, padx=20)
        
        self.create_doctor_table(table_frame)
        self.view_doctors()
    
    def create_doctor_form(self, parent):
        fields = [
            ("Doctor ID:", "entry_did", lambda x: ValidationUtils.validate_id(x, "Doctor ID")),
            ("First Name:", "entry_dfname", ValidationUtils.validate_name),
            ("Last Name:", "entry_dlname", ValidationUtils.validate_name),
            ("Specialization:", "entry_spec", lambda x: ValidationUtils.validate_not_empty(x, "Specialization")),
            ("Phone:", "entry_dph", ValidationUtils.validate_phone),
            ("Email:", "entry_demail", ValidationUtils.validate_email)
        ]
        
        for i, (label_text, entry_name, validation_func) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(parent, text=label_text, font=self.body_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).grid(row=row, column=col, padx=10, pady=5, sticky="w")
            entry = ModernEntry(parent, validation_func=validation_func, width=25)
            entry.grid(row=row, column=col+1, padx=10, pady=5)
            setattr(self, entry_name, entry)
    
    def create_doctor_table(self, parent):
        tk.Label(parent, text="Doctor Records", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack(pady=(15, 10))
        tree_frame = tk.Frame(parent, bg=ModernColors.SURFACE)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        self.tree_doctor = ttk.Treeview(tree_frame, columns=("DID", "F_NAME", "L_NAME", "SPEC", "PH", "EMAIL"), show="headings", yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.configure(command=self.tree_doctor.yview)
        h_scrollbar.configure(command=self.tree_doctor.xview)
        headings = [("DID", "Doctor ID", 100), ("F_NAME", "First Name", 120), ("L_NAME", "Last Name", 120), ("SPEC", "Specialization", 150), ("PH", "Phone", 120), ("EMAIL", "Email", 200)]
        for col, heading, width in headings:
            self.tree_doctor.heading(col, text=heading)
            self.tree_doctor.column(col, width=width, minwidth=80)
        self.tree_doctor.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree_doctor.bind('<<TreeviewSelect>>', self.on_doctor_select)

    def on_doctor_select(self, event):
        if self.tree_doctor.selection():
            item = self.tree_doctor.selection()[0]
            values = self.tree_doctor.item(item, 'values')
            entries = [self.entry_did, self.entry_dfname, self.entry_dlname, self.entry_spec, self.entry_dph, self.entry_demail]
            for i, entry in enumerate(entries):
                entry.delete(0, tk.END)
                if i < len(values):
                    entry.insert(0, values[i])
    
    def add_doctor(self):
        try:
            is_valid_id, msg_id = ValidationUtils.validate_id(self.entry_did.get_value(), "Doctor ID")
            if not is_valid_id: messagebox.showerror("Validation Error", msg_id); return
            is_valid_fname, msg_fname = ValidationUtils.validate_name(self.entry_dfname.get_value())
            if not is_valid_fname: messagebox.showerror("Validation Error", msg_fname); return
            is_valid_lname, msg_lname = ValidationUtils.validate_name(self.entry_dlname.get_value())
            if not is_valid_lname: messagebox.showerror("Validation Error", msg_lname); return
            is_valid_spec, msg_spec = ValidationUtils.validate_not_empty(self.entry_spec.get_value(), "Specialization")
            if not is_valid_spec: messagebox.showerror("Validation Error", msg_spec); return
            is_valid_ph, clean_ph = ValidationUtils.validate_phone(self.entry_dph.get_value())
            if not is_valid_ph: messagebox.showerror("Validation Error", clean_ph); return
            
            csr.execute("INSERT INTO DOCTOR (DID, F_NAME, L_NAME, SPEC, PH, EMAIL) VALUES (%s, %s, %s, %s, %s, %s)",
                        (self.entry_did.get_value(), self.entry_dfname.get_value(), self.entry_dlname.get_value(),
                         self.entry_spec.get_value(), clean_ph, self.entry_demail.get_value()))
            conn.commit()
            messagebox.showinfo("Success", "Doctor added successfully!")
            self.clear_doctor_form()
            self.view_doctors()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error adding doctor: {str(e)}")

    def update_doctor(self):
        if not self.tree_doctor.selection(): messagebox.showerror("Error", "Please select a doctor to update"); return
        try:
            selected_item = self.tree_doctor.selection()[0]
            old_did = self.tree_doctor.item(selected_item, 'values')[0]
            is_valid_id, msg_id = ValidationUtils.validate_id(self.entry_did.get_value(), "Doctor ID")
            if not is_valid_id: messagebox.showerror("Validation Error", msg_id); return
            is_valid_fname, msg_fname = ValidationUtils.validate_name(self.entry_dfname.get_value())
            if not is_valid_fname: messagebox.showerror("Validation Error", msg_fname); return
            is_valid_ph, clean_ph = ValidationUtils.validate_phone(self.entry_dph.get_value())
            if not is_valid_ph: messagebox.showerror("Validation Error", clean_ph); return

            csr.execute("UPDATE DOCTOR SET DID=%s, F_NAME=%s, L_NAME=%s, SPEC=%s, PH=%s, EMAIL=%s WHERE DID=%s",
                        (self.entry_did.get_value(), self.entry_dfname.get_value(), self.entry_dlname.get_value(),
                         self.entry_spec.get_value(), clean_ph, self.entry_demail.get_value(), old_did))
            conn.commit()
            messagebox.showinfo("Success", "Doctor updated successfully!")
            self.view_doctors()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error updating doctor: {str(e)}")
    
    def delete_doctor(self):
        if not self.tree_doctor.selection(): messagebox.showerror("Error", "Please select a doctor to delete"); return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this doctor?"):
            try:
                selected_item = self.tree_doctor.selection()[0]
                did = self.tree_doctor.item(selected_item, 'values')[0]
                csr.execute("DELETE FROM DOCTOR WHERE DID=%s", (did,))
                conn.commit()
                self.tree_doctor.delete(selected_item)
                messagebox.showinfo("Success", "Doctor deleted successfully!")
                self.clear_doctor_form()
            except Exception as e:
                messagebox.showerror("Database Error", f"Error deleting doctor: {str(e)}")

    def clear_doctor_form(self):
        entries = [self.entry_did, self.entry_dfname, self.entry_dlname, self.entry_spec, self.entry_dph, self.entry_demail]
        for entry in entries:
            entry.delete(0, tk.END)

    def view_doctors(self):
        try:
            for row in self.tree_doctor.get_children(): self.tree_doctor.delete(row)
            csr.execute("SELECT * FROM DOCTOR")
            rows = csr.fetchall()
            for row in rows: self.tree_doctor.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading doctors: {str(e)}")
    
    def search_doctor(self):
        try:
            for row in self.tree_doctor.get_children(): self.tree_doctor.delete(row)
            search_field = self.search_field_doctor.get()
            search_value = self.search_entry_doctor.get_value()
            if not search_field or not search_value: messagebox.showerror("Error", "Please select search field and enter search value"); return
            # Correctly use parameterized query
            query = f"SELECT * FROM DOCTOR WHERE {search_field} LIKE %s"
            csr.execute(query, (f"%{search_value}%",))
            rows = csr.fetchall()
            for row in rows: self.tree_doctor.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Database Error", f"Error searching doctors: {str(e)}")

    # ------------------ DEPARTMENT MANAGEMENT ------------------
    def show_departments(self):
        self.clear_main_frame()
        self.highlight_nav_button(2)
        
        department_frame = tk.Frame(self.main_frame, bg=ModernColors.BACKGROUND)
        department_frame.pack(fill="both", expand=True)
        
        tk.Label(department_frame, text="🏢 Department Management", font=self.heading_font, bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(pady=(0, 10))
        
        form_frame = tk.Frame(department_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # MODIFIED: Reduced ipady and pady to make form section smaller.
        form_frame.pack(fill="x", pady=(0, 10), padx=20, ipady=10)
        
        tk.Label(form_frame, text="Add/Update Department", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack(pady=(5, 10))
        
        fields_frame = tk.Frame(form_frame, bg=ModernColors.SURFACE)
        fields_frame.pack(padx=40)
        self.create_department_form(fields_frame)
        
        button_frame = tk.Frame(form_frame, bg=ModernColors.SURFACE)
        button_frame.pack(pady=10)
        
        ModernButton(button_frame, "Add Department", self.add_department, "primary").pack(side="left", padx=5)
        ModernButton(button_frame, "Update Department", self.update_department, "secondary").pack(side="left", padx=5)
        ModernButton(button_frame, "Delete Department", self.delete_department, "danger").pack(side="left", padx=5)
        ModernButton(button_frame, "Clear Form", self.clear_department_form, "warning").pack(side="left", padx=5)

        search_frame = tk.Frame(department_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # MODIFIED: Reduced ipady and pady to make search section smaller.
        search_frame.pack(fill="x", pady=(0, 10), padx=20, ipady=5)
        tk.Label(search_frame, text="Search Departments", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack()
        search_controls = tk.Frame(search_frame, bg=ModernColors.SURFACE)
        search_controls.pack(pady=5)
        self.search_field_department = ttk.Combobox(search_controls, values=["DepID", "D_NAME", "FLOOR", "TELEPHONE"], font=self.body_font, width=15)
        self.search_field_department.pack(side="left", padx=5)
        self.search_field_department.set("D_NAME")
        self.search_entry_department = ModernEntry(search_controls, placeholder="Search...", width=25)
        self.search_entry_department.pack(side="left", padx=5)
        ModernButton(search_controls, "Search", self.search_department, "primary").pack(side="left", padx=5)
        ModernButton(search_controls, "View All", self.view_departments, "secondary").pack(side="left", padx=5)

        table_frame = tk.Frame(department_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # The table now has more vertical space to expand into.
        table_frame.pack(fill="both", expand=True, padx=20)
        self.create_department_table(table_frame)
        self.view_departments()

    def create_department_form(self, parent):
        fields = [
            ("Department ID:", "entry_depid", lambda x: ValidationUtils.validate_id(x, "Department ID")),
            ("Department Name:", "entry_dname", lambda x: ValidationUtils.validate_not_empty(x, "Department Name")),
            ("Floor:", "entry_floor", lambda x: ValidationUtils.validate_id(x, "Floor")),
            ("Telephone:", "entry_dtelephone", ValidationUtils.validate_phone)
        ]
        
        for i, (label_text, entry_name, validation_func) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(parent, text=label_text, font=self.body_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).grid(row=row, column=col, padx=10, pady=5, sticky="w")
            entry = ModernEntry(parent, validation_func=validation_func, width=25)
            entry.grid(row=row, column=col+1, padx=10, pady=5)
            setattr(self, entry_name, entry)
    
    def create_department_table(self, parent):
        tk.Label(parent, text="Department Records", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack(pady=(15, 10))
        tree_frame = tk.Frame(parent, bg=ModernColors.SURFACE)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        self.tree_department = ttk.Treeview(tree_frame, columns=("DepID", "D_NAME", "FLOOR", "TELEPHONE"), show="headings", yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.configure(command=self.tree_department.yview)
        h_scrollbar.configure(command=self.tree_department.xview)
        headings = [("DepID", "Dept ID", 100), ("D_NAME", "Dept Name", 200), ("FLOOR", "Floor", 100), ("TELEPHONE", "Telephone", 150)]
        for col, heading, width in headings:
            self.tree_department.heading(col, text=heading)
            self.tree_department.column(col, width=width, minwidth=80)
        self.tree_department.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree_department.bind('<<TreeviewSelect>>', self.on_department_select)
    
    def on_department_select(self, event):
        if self.tree_department.selection():
            item = self.tree_department.selection()[0]
            values = self.tree_department.item(item, 'values')
            entries = [self.entry_depid, self.entry_dname, self.entry_floor, self.entry_dtelephone]
            for i, entry in enumerate(entries):
                entry.delete(0, tk.END)
                if i < len(values):
                    entry.insert(0, values[i])

    def add_department(self):
        try:
            is_valid_id, msg_id = ValidationUtils.validate_id(self.entry_depid.get_value(), "Department ID")
            if not is_valid_id: messagebox.showerror("Validation Error", msg_id); return
            is_valid_name, msg_name = ValidationUtils.validate_not_empty(self.entry_dname.get_value(), "Department Name")
            if not is_valid_name: messagebox.showerror("Validation Error", msg_name); return
            is_valid_floor, msg_floor = ValidationUtils.validate_id(self.entry_floor.get_value(), "Floor")
            if not is_valid_floor: messagebox.showerror("Validation Error", msg_floor); return
            is_valid_phone, clean_phone = ValidationUtils.validate_phone(self.entry_dtelephone.get_value())
            if not is_valid_phone: messagebox.showerror("Validation Error", clean_phone); return
            
            csr.execute("INSERT INTO DEPT (DepID, D_NAME, FLOOR, TELEPHONE) VALUES (%s, %s, %s, %s)",
                        (self.entry_depid.get_value(), self.entry_dname.get_value(), self.entry_floor.get_value(), clean_phone))
            conn.commit()
            messagebox.showinfo("Success", "Department added successfully!")
            self.clear_department_form()
            self.view_departments()
        except Exception as e: messagebox.showerror("Database Error", f"Error adding department: {str(e)}")

    def update_department(self):
        if not self.tree_department.selection(): messagebox.showerror("Error", "Please select a department to update"); return
        try:
            selected_item = self.tree_department.selection()[0]
            old_depid = self.tree_department.item(selected_item, 'values')[0]
            is_valid_id, msg_id = ValidationUtils.validate_id(self.entry_depid.get_value(), "Department ID")
            if not is_valid_id: messagebox.showerror("Validation Error", msg_id); return
            is_valid_name, msg_name = ValidationUtils.validate_not_empty(self.entry_dname.get_value(), "Department Name")
            if not is_valid_name: messagebox.showerror("Validation Error", msg_name); return
            is_valid_floor, msg_floor = ValidationUtils.validate_id(self.entry_floor.get_value(), "Floor")
            if not is_valid_floor: messagebox.showerror("Validation Error", msg_floor); return
            is_valid_phone, clean_phone = ValidationUtils.validate_phone(self.entry_dtelephone.get_value())
            if not is_valid_phone: messagebox.showerror("Validation Error", clean_phone); return

            csr.execute("UPDATE DEPT SET DepID=%s, D_NAME=%s, FLOOR=%s, TELEPHONE=%s WHERE DepID=%s",
                        (self.entry_depid.get_value(), self.entry_dname.get_value(), self.entry_floor.get_value(), clean_phone, old_depid))
            conn.commit()
            messagebox.showinfo("Success", "Department updated successfully!")
            self.view_departments()
        except Exception as e: messagebox.showerror("Database Error", f"Error updating department: {str(e)}")
    
    def delete_department(self):
        if not self.tree_department.selection(): messagebox.showerror("Error", "Please select a department to delete"); return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this department?"):
            try:
                selected_item = self.tree_department.selection()[0]
                depid = self.tree_department.item(selected_item, 'values')[0]
                csr.execute("DELETE FROM DEPT WHERE DepID=%s", (depid,))
                conn.commit()
                self.tree_department.delete(selected_item)
                messagebox.showinfo("Success", "Department deleted successfully!")
                self.clear_department_form()
            except Exception as e: messagebox.showerror("Database Error", f"Error deleting department: {str(e)}")

    def clear_department_form(self):
        entries = [self.entry_depid, self.entry_dname, self.entry_floor, self.entry_dtelephone]
        for entry in entries: entry.delete(0, tk.END)

    def view_departments(self):
        try:
            for row in self.tree_department.get_children(): self.tree_department.delete(row)
            csr.execute("SELECT * FROM DEPT")
            rows = csr.fetchall()
            for row in rows: self.tree_department.insert("", tk.END, values=row)
        except Exception as e: messagebox.showerror("Database Error", f"Error loading departments: {str(e)}")

    def search_department(self):
        try:
            for row in self.tree_department.get_children(): self.tree_department.delete(row)
            search_field = self.search_field_department.get()
            search_value = self.search_entry_department.get_value()
            if not search_field or not search_value: messagebox.showerror("Error", "Please select search field and enter search value"); return
            # Correctly use parameterized query
            query = f"SELECT * FROM DEPT WHERE {search_field} LIKE %s"
            csr.execute(query, (f"%{search_value}%",))
            rows = csr.fetchall()
            for row in rows: self.tree_department.insert("", tk.END, values=row)
        except Exception as e: messagebox.showerror("Database Error", f"Error searching departments: {str(e)}")

    # ------------------ APPOINTMENT MANAGEMENT ------------------
    def show_appointments(self):
        self.clear_main_frame()
        self.highlight_nav_button(3)
        
        appointment_frame = tk.Frame(self.main_frame, bg=ModernColors.BACKGROUND)
        appointment_frame.pack(fill="both", expand=True)
        tk.Label(appointment_frame, text="📅 Appointment Scheduling", font=self.heading_font, bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(pady=(0, 10))
        
        form_frame = tk.Frame(appointment_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # MODIFIED: Reduced ipady and pady to make form section smaller.
        form_frame.pack(fill="x", pady=(0, 10), padx=20, ipady=10)
        tk.Label(form_frame, text="Add/Update Appointment", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack(pady=(5, 10))
        
        fields_frame = tk.Frame(form_frame, bg=ModernColors.SURFACE)
        fields_frame.pack(padx=40)
        self.create_appointment_form(fields_frame)
        
        button_frame = tk.Frame(form_frame, bg=ModernColors.SURFACE)
        button_frame.pack(pady=10)
        ModernButton(button_frame, "Add Appointment", self.add_appointment, "primary").pack(side="left", padx=5)
        ModernButton(button_frame, "Update Appointment", self.update_appointment, "secondary").pack(side="left", padx=5)
        ModernButton(button_frame, "Delete Appointment", self.delete_appointment, "danger").pack(side="left", padx=5)
        ModernButton(button_frame, "Clear Form", self.clear_appointment_form, "warning").pack(side="left", padx=5)

        search_frame = tk.Frame(appointment_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # MODIFIED: Reduced ipady and pady to make search section smaller.
        search_frame.pack(fill="x", pady=(0, 10), padx=20, ipady=5)
        tk.Label(search_frame, text="Search Appointments", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack()
        search_controls = tk.Frame(search_frame, bg=ModernColors.SURFACE)
        search_controls.pack(pady=5)
        self.search_field_appointment = ttk.Combobox(search_controls, values=["AID", "PID", "DID", "DepID", "A_DATE"], font=self.body_font, width=15)
        self.search_field_appointment.pack(side="left", padx=5)
        self.search_field_appointment.set("PID")
        self.search_entry_appointment = ModernEntry(search_controls, placeholder="Search...", width=25)
        self.search_entry_appointment.pack(side="left", padx=5)
        ModernButton(search_controls, "Search", self.search_appointment, "primary").pack(side="left", padx=5)
        ModernButton(search_controls, "View All", self.view_appointments, "secondary").pack(side="left", padx=5)

        table_frame = tk.Frame(appointment_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # The table now has more vertical space to expand into.
        table_frame.pack(fill="both", expand=True, padx=20)
        self.create_appointment_table(table_frame)
        self.view_appointments()
    
    def create_appointment_form(self, parent):
        fields = [
            ("Appointment ID:", "entry_aid", lambda x: ValidationUtils.validate_id(x, "Appointment ID")),
            ("Patient ID:", "entry_apid", lambda x: ValidationUtils.validate_id(x, "Patient ID")),
            ("Doctor ID:", "entry_adid", lambda x: ValidationUtils.validate_id(x, "Doctor ID")),
            ("Date (YYYY-MM-DD):", "entry_adate", ValidationUtils.validate_date),
            ("Time (HH:MM):", "entry_atime", ValidationUtils.validate_time),
            ("Department ID:", "entry_adepid", lambda x: ValidationUtils.validate_id(x, "Department ID"))
        ]
        
        for i, (label_text, entry_name, validation_func) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(parent, text=label_text, font=self.body_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).grid(row=row, column=col, padx=10, pady=5, sticky="w")
            entry = ModernEntry(parent, validation_func=validation_func, width=25)
            entry.grid(row=row, column=col+1, padx=10, pady=5)
            setattr(self, entry_name, entry)

    def create_appointment_table(self, parent):
        tk.Label(parent, text="Appointment Records", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack(pady=(15, 10))
        tree_frame = tk.Frame(parent, bg=ModernColors.SURFACE)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        self.tree_appointment = ttk.Treeview(tree_frame, columns=("AID", "PID", "DID", "A_DATE", "A_TIME", "DepID"), show="headings", yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.configure(command=self.tree_appointment.yview)
        h_scrollbar.configure(command=self.tree_appointment.xview)
        headings = [("AID", "Appt ID", 100), ("PID", "Patient ID", 100), ("DID", "Doctor ID", 100), ("A_DATE", "Date", 120), ("A_TIME", "Time", 100), ("DepID", "Dept ID", 100)]
        for col, heading, width in headings:
            self.tree_appointment.heading(col, text=heading)
            self.tree_appointment.column(col, width=width, minwidth=80)
        self.tree_appointment.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree_appointment.bind('<<TreeviewSelect>>', self.on_appointment_select)

    def on_appointment_select(self, event):
        if self.tree_appointment.selection():
            item = self.tree_appointment.selection()[0]
            values = self.tree_appointment.item(item, 'values')
            entries = [self.entry_aid, self.entry_apid, self.entry_adid, self.entry_adate, self.entry_atime, self.entry_adepid]
            for i, entry in enumerate(entries):
                entry.delete(0, tk.END)
                if i < len(values):
                    entry.insert(0, values[i])

    def add_appointment(self):
        try:
            # Check if PID, DID, and DepID exist
            csr.execute("SELECT COUNT(*) FROM PATIENT WHERE PID = %s", (self.entry_apid.get_value(),))
            if csr.fetchone()[0] == 0: messagebox.showerror("Error", "Patient ID not found."); return
            csr.execute("SELECT COUNT(*) FROM DOCTOR WHERE DID = %s", (self.entry_adid.get_value(),))
            if csr.fetchone()[0] == 0: messagebox.showerror("Error", "Doctor ID not found."); return
            csr.execute("SELECT COUNT(*) FROM DEPT WHERE DepID = %s", (self.entry_adepid.get_value(),))
            if csr.fetchone()[0] == 0: messagebox.showerror("Error", "Department ID not found."); return
            
            csr.execute("INSERT INTO APPOINTMENT (AID, PID, DID, A_DATE, A_TIME, DepID) VALUES (%s, %s, %s, %s, %s, %s)",
                        (self.entry_aid.get_value(), self.entry_apid.get_value(), self.entry_adid.get_value(),
                         self.entry_adate.get_value(), self.entry_atime.get_value(), self.entry_adepid.get_value()))
            conn.commit()
            messagebox.showinfo("Success", "Appointment added successfully!")
            self.clear_appointment_form()
            self.view_appointments()
        except Exception as e: messagebox.showerror("Database Error", f"Error adding appointment: {str(e)}")
    
    def update_appointment(self):
        if not self.tree_appointment.selection(): messagebox.showerror("Error", "Please select an appointment to update"); return
        try:
            selected_item = self.tree_appointment.selection()[0]
            old_aid = self.tree_appointment.item(selected_item, 'values')[0]
            csr.execute("UPDATE APPOINTMENT SET AID=%s, PID=%s, DID=%s, A_DATE=%s, A_TIME=%s, DepID=%s WHERE AID=%s",
                        (self.entry_aid.get_value(), self.entry_apid.get_value(), self.entry_adid.get_value(),
                         self.entry_adate.get_value(), self.entry_atime.get_value(), self.entry_adepid.get_value(), old_aid))
            conn.commit()
            messagebox.showinfo("Success", "Appointment updated successfully!")
            self.view_appointments()
        except Exception as e: messagebox.showerror("Database Error", f"Error updating appointment: {str(e)}")

    def delete_appointment(self):
        if not self.tree_appointment.selection(): messagebox.showerror("Error", "Please select an appointment to delete"); return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this appointment?"):
            try:
                selected_item = self.tree_appointment.selection()[0]
                aid = self.tree_appointment.item(selected_item, 'values')[0]
                csr.execute("DELETE FROM APPOINTMENT WHERE AID=%s", (aid,))
                conn.commit()
                self.tree_appointment.delete(selected_item)
                messagebox.showinfo("Success", "Appointment deleted successfully!")
                self.clear_appointment_form()
            except Exception as e: messagebox.showerror("Database Error", f"Error deleting appointment: {str(e)}")

    def clear_appointment_form(self):
        entries = [self.entry_aid, self.entry_apid, self.entry_adid, self.entry_adate, self.entry_atime, self.entry_adepid]
        for entry in entries: entry.delete(0, tk.END)

    def view_appointments(self):
        try:
            for row in self.tree_appointment.get_children(): self.tree_appointment.delete(row)
            csr.execute("SELECT * FROM APPOINTMENT")
            rows = csr.fetchall()
            for row in rows: self.tree_appointment.insert("", tk.END, values=row)
        except Exception as e: messagebox.showerror("Database Error", f"Error loading appointments: {str(e)}")

    def search_appointment(self):
        try:
            for row in self.tree_appointment.get_children(): self.tree_appointment.delete(row)
            search_field = self.search_field_appointment.get()
            search_value = self.search_entry_appointment.get_value()
            if not search_field or not search_value: messagebox.showerror("Error", "Please select search field and enter search value"); return
            # Correctly use parameterized query
            query = f"SELECT * FROM APPOINTMENT WHERE {search_field} LIKE %s"
            csr.execute(query, (f"%{search_value}%",))
            rows = csr.fetchall()
            for row in rows: self.tree_appointment.insert("", tk.END, values=row)
        except Exception as e: messagebox.showerror("Database Error", f"Error searching appointments: {str(e)}")

    # ------------------ MEDICAL RECORDS MANAGEMENT ------------------
    def show_medical_records(self):
        self.clear_main_frame()
        self.highlight_nav_button(4)
        
        medical_record_frame = tk.Frame(self.main_frame, bg=ModernColors.BACKGROUND)
        medical_record_frame.pack(fill="both", expand=True)
        tk.Label(medical_record_frame, text="📋 Medical Records", font=self.heading_font, bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(pady=(0, 10))
        
        form_frame = tk.Frame(medical_record_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # MODIFIED: Reduced ipady and pady to make form section smaller.
        form_frame.pack(fill="x", pady=(0, 10), padx=20, ipady=10)
        tk.Label(form_frame, text="Add/Update Medical Record", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack(pady=(5, 10))
        
        fields_frame = tk.Frame(form_frame, bg=ModernColors.SURFACE)
        fields_frame.pack(padx=40)
        self.create_medical_record_form(fields_frame)
        
        button_frame = tk.Frame(form_frame, bg=ModernColors.SURFACE)
        button_frame.pack(pady=10)
        ModernButton(button_frame, "Add Record", self.add_medical_record, "primary").pack(side="left", padx=5)
        ModernButton(button_frame, "Update Record", self.update_medical_record, "secondary").pack(side="left", padx=5)
        ModernButton(button_frame, "Delete Record", self.delete_medical_record, "danger").pack(side="left", padx=5)
        ModernButton(button_frame, "Clear Form", self.clear_medical_record_form, "warning").pack(side="left", padx=5)

        search_frame = tk.Frame(medical_record_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # MODIFIED: Reduced ipady and pady to make search section smaller.
        search_frame.pack(fill="x", pady=(0, 10), padx=20, ipady=5)
        tk.Label(search_frame, text="Search Records", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack()
        search_controls = tk.Frame(search_frame, bg=ModernColors.SURFACE)
        search_controls.pack(pady=5)
        self.search_field_medrecord = ttk.Combobox(search_controls, values=["RID", "PID", "DID", "LAST_VISIT"], font=self.body_font, width=15)
        self.search_field_medrecord.pack(side="left", padx=5)
        self.search_field_medrecord.set("RID")
        self.search_entry_medrecord = ModernEntry(search_controls, placeholder="Search...", width=25)
        self.search_entry_medrecord.pack(side="left", padx=5)
        ModernButton(search_controls, "Search", self.search_medical_record, "primary").pack(side="left", padx=5)
        ModernButton(search_controls, "View All", self.view_medical_records, "secondary").pack(side="left", padx=5)

        table_frame = tk.Frame(medical_record_frame, bg=ModernColors.SURFACE, relief="solid", bd=1)
        # The table now has more vertical space to expand into.
        table_frame.pack(fill="both", expand=True, padx=20)
        self.create_medical_record_table(table_frame)
        self.view_medical_records()

    def create_medical_record_form(self, parent):
        fields = [
            ("Record ID:", "entry_rid", lambda x: ValidationUtils.validate_id(x, "Record ID")),
            ("Patient ID:", "entry_rpid", lambda x: ValidationUtils.validate_id(x, "Patient ID")),
            ("Doctor ID:", "entry_rdid", lambda x: ValidationUtils.validate_id(x, "Doctor ID")),
            ("Last Visit (YYYY-MM-DD):", "entry_last_visit", ValidationUtils.validate_date)
        ]
        
        for i, (label_text, entry_name, validation_func) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(parent, text=label_text, font=self.body_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).grid(row=row, column=col, padx=10, pady=5, sticky="w")
            entry = ModernEntry(parent, validation_func=validation_func, width=25)
            entry.grid(row=row, column=col+1, padx=10, pady=5)
            setattr(self, entry_name, entry)
        
        tk.Label(parent, text="Diagnosis:", font=self.body_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # MODIFIED: Added a scrollbar to the diagnosis text box and reduced its height
        text_frame = tk.Frame(parent, bg=ModernColors.SURFACE)
        text_frame.grid(row=2, column=1, columnspan=3, padx=10, pady=5, sticky="ew")
        
        self.text_diagnosis = tk.Text(text_frame, font=self.body_font, width=40, height=3, wrap="word")
        self.text_diagnosis.pack(side="left", fill="both", expand=True)
        
        text_scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.text_diagnosis.yview)
        text_scrollbar.pack(side="right", fill="y")
        self.text_diagnosis.config(yscrollcommand=text_scrollbar.set)
        
    def create_medical_record_table(self, parent):
        tk.Label(parent, text="Medical Records", font=self.subheading_font, bg=ModernColors.SURFACE, fg=ModernColors.TEXT_PRIMARY).pack(pady=(15, 10))
        tree_frame = tk.Frame(parent, bg=ModernColors.SURFACE)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        self.tree_medrecord = ttk.Treeview(tree_frame, columns=("RID", "PID", "DID", "LAST_VISIT", "DIAGNOSIS"), show="headings", yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.configure(command=self.tree_medrecord.yview)
        h_scrollbar.configure(command=self.tree_medrecord.xview)
        headings = [("RID", "Record ID", 100), ("PID", "Patient ID", 100), ("DID", "Doctor ID", 100), ("LAST_VISIT", "Last Visit", 120), ("DIAGNOSIS", "Diagnosis", 400)]
        for col, heading, width in headings:
            self.tree_medrecord.heading(col, text=heading)
            self.tree_medrecord.column(col, width=width, minwidth=80)
        self.tree_medrecord.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree_medrecord.bind('<<TreeviewSelect>>', self.on_medrecord_select)
    
    def on_medrecord_select(self, event):
        if self.tree_medrecord.selection():
            item = self.tree_medrecord.selection()[0]
            values = self.tree_medrecord.item(item, 'values')
            entries = [self.entry_rid, self.entry_rpid, self.entry_rdid, self.entry_last_visit]
            for i, entry in enumerate(entries):
                entry.delete(0, tk.END)
                if i < len(values): entry.insert(0, values[i])
            self.text_diagnosis.delete(1.0, tk.END)
            if len(values) > 4: self.text_diagnosis.insert(1.0, values[4])

    def add_medical_record(self):
        try:
            csr.execute("INSERT INTO MED_RECORD (RID, PID, DID, LAST_VISIT, DIAGNOSIS) VALUES (%s, %s, %s, %s, %s)",
                        (self.entry_rid.get_value(), self.entry_rpid.get_value(), self.entry_rdid.get_value(),
                         self.entry_last_visit.get_value(), self.text_diagnosis.get(1.0, tk.END).strip()))
            conn.commit()
            messagebox.showinfo("Success", "Medical Record added successfully!")
            self.clear_medical_record_form()
            self.view_medical_records()
        except Exception as e: messagebox.showerror("Database Error", f"Error adding medical record: {str(e)}")

    def update_medical_record(self):
        if not self.tree_medrecord.selection(): messagebox.showerror("Error", "Please select a medical record to update"); return
        try:
            selected_item = self.tree_medrecord.selection()[0]
            old_rid = self.tree_medrecord.item(selected_item, 'values')[0]
            csr.execute("UPDATE MED_RECORD SET RID=%s, PID=%s, DID=%s, LAST_VISIT=%s, DIAGNOSIS=%s WHERE RID=%s",
                        (self.entry_rid.get_value(), self.entry_rpid.get_value(), self.entry_rdid.get_value(),
                         self.entry_last_visit.get_value(), self.text_diagnosis.get(1.0, tk.END).strip(), old_rid))
            conn.commit()
            messagebox.showinfo("Success", "Medical Record updated successfully!")
            self.view_medical_records()
        except Exception as e: messagebox.showerror("Database Error", f"Error updating medical record: {str(e)}")
    
    def delete_medical_record(self):
        if not self.tree_medrecord.selection(): messagebox.showerror("Error", "Please select a medical record to delete"); return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            try:
                selected_item = self.tree_medrecord.selection()[0]
                rid = self.tree_medrecord.item(selected_item, 'values')[0]
                csr.execute("DELETE FROM MED_RECORD WHERE RID=%s", (rid,))
                conn.commit()
                self.tree_medrecord.delete(selected_item)
                messagebox.showinfo("Success", "Medical Record deleted successfully!")
                self.clear_medical_record_form()
            except Exception as e: messagebox.showerror("Database Error", f"Error deleting medical record: {str(e)}")

    def clear_medical_record_form(self):
        entries = [self.entry_rid, self.entry_rpid, self.entry_rdid, self.entry_last_visit]
        for entry in entries: entry.delete(0, tk.END)
        self.text_diagnosis.delete(1.0, tk.END)

    def view_medical_records(self):
        try:
            for row in self.tree_medrecord.get_children(): self.tree_medrecord.delete(row)
            csr.execute("SELECT * FROM MED_RECORD")
            rows = csr.fetchall()
            for row in rows: self.tree_medrecord.insert("", tk.END, values=row)
        except Exception as e: messagebox.showerror("Database Error", f"Error loading medical records: {str(e)}")

    def search_medical_record(self):
        try:
            for row in self.tree_medrecord.get_children(): self.tree_medrecord.delete(row)
            search_field = self.search_field_medrecord.get()
            search_value = self.search_entry_medrecord.get_value()
            if not search_field or not search_value: messagebox.showerror("Error", "Please select search field and enter search value"); return
            # Correctly use parameterized query
            query = f"SELECT * FROM MED_RECORD WHERE {search_field} LIKE %s"
            csr.execute(query, (f"%{search_value}%",))
            rows = csr.fetchall()
            for row in rows: self.tree_medrecord.insert("", tk.END, values=row)
        except Exception as e: messagebox.showerror("Database Error", f"Error searching medical records: {str(e)}")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                if conn.is_connected():
                    conn.close()
            except Exception as e:
                pass
            self.root.destroy()

# Main entry point for the application
if __name__ == "__main__":
    app = ModernHospitalManagement()