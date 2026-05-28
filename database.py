"""
database.py
-----------
Handles connection to the SQLite database, schema initialization, mock data seeding,
and full CRUD data access layers for the computer coaching management system.
"""

import sqlite3
import os
import hashlib
from datetime import datetime

DB_NAME = "coaching_management.db"

def get_connection():
    """Returns a connection to the SQLite database with dict-like row factory."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """Hashes a password local security with SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def initialize_db():
    """Creates the SQLite database, schema, and rolls in default seed records."""
    db_already_exists = os.path.exists(DB_NAME)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 2. Schema DDL
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        user_type TEXT NOT NULL CHECK (user_type IN ('Admin', 'Staff', 'Student')),
        gender TEXT NOT NULL,
        profile_pic_path TEXT,
        address TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT UNIQUE NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT NOT NULL,
        course_id INTEGER NOT NULL,
        staff_id INTEGER NOT NULL,
        FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
        FOREIGN KEY (staff_id) REFERENCES staff (id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        course_id INTEGER NOT NULL,
        session_start TEXT NOT NULL,
        session_end TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        course_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('Present', 'Absent')),
        attendance_date TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,
        UNIQUE(student_id, subject_id, attendance_date)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        marks_obtained REAL NOT NULL,
        max_marks REAL NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,
        UNIQUE(student_id, subject_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        reply_text TEXT,
        created_at TEXT NOT NULL,
        replied_at TEXT,
        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        leave_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected')),
        FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()

    # 3. Seed Default Records
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Admin account
        adm_hash = hash_password("admin123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, first_name, last_name, email, user_type, gender, address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, ("admin", adm_hash, "System", "Administrator", "admin@coaching.com", "Admin", "Male", "Main Campus, Building A", now_str))
        
        # Staff account (Kumar, Rohit)
        fac_hash = hash_password("faculty123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, first_name, last_name, email, user_type, gender, address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, ("rohit", fac_hash, "Rohit", "Kumar", "rohit.kumar@coaching.com", "Staff", "Male", "45 Park Avenue, Delhi", now_str))
        staff_user_id = cursor.lastrowid
        
        # Student 1 (Sharma, Amit)
        stu1_hash = hash_password("student123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, first_name, last_name, email, user_type, gender, address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, ("amit", stu1_hash, "Amit", "Sharma", "amit.sharma@coaching.com", "Student", "Male", "Sector 15, Rohini, Delhi", now_str))
        stu1_user_id = cursor.lastrowid

        # Student 2 (Varma, Pooja)
        stu2_hash = hash_password("student123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, first_name, last_name, email, user_type, gender, address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, ("pooja", stu2_hash, "Pooja", "Varma", "pooja.varma@coaching.com", "Student", "Female", "H-32, Dwarka, Delhi", now_str))
        stu2_user_id = cursor.lastrowid

        # Courses
        cursor.execute("INSERT INTO courses (course_name) VALUES (?);", ("BCA",))
        bca_id = cursor.lastrowid
        cursor.execute("INSERT INTO courses (course_name) VALUES (?);", ("MCA",))
        mca_id = cursor.lastrowid
        cursor.execute("INSERT INTO courses (course_name) VALUES (?);", ("B.Tech Computer Science",))

        # Link Staff to BCA course
        cursor.execute("INSERT INTO staff (user_id, course_id) VALUES (?, ?);", (staff_user_id, bca_id))
        staff_row_id = cursor.lastrowid

        # Link Student 1 and 2 to BCA course
        cursor.execute("INSERT INTO students (user_id, course_id, session_start, session_end) VALUES (?, ?, ?, ?);", 
                       (stu1_user_id, bca_id, "2025-01-01", "2028-01-01"))
        stu1_row_id = cursor.lastrowid
        cursor.execute("INSERT INTO students (user_id, course_id, session_start, session_end) VALUES (?, ?, ?, ?);", 
                       (stu2_user_id, bca_id, "2025-01-01", "2028-01-01"))
        stu2_row_id = cursor.lastrowid

        # Subjects
        cursor.execute("INSERT INTO subjects (subject_name, course_id, staff_id) VALUES (?, ?, ?);", ("Python Programming", bca_id, staff_row_id))
        python_sub_id = cursor.lastrowid
        cursor.execute("INSERT INTO subjects (subject_name, course_id, staff_id) VALUES (?, ?, ?);", ("Data Structures", bca_id, staff_row_id))
        ds_sub_id = cursor.lastrowid

        # Attendance Seed Data
        cursor.execute("INSERT INTO attendance (student_id, subject_id, status, attendance_date) VALUES (?, ?, ?, ?);", 
                       (stu1_row_id, python_sub_id, "Present", "2026-05-25"))
        cursor.execute("INSERT INTO attendance (student_id, subject_id, status, attendance_date) VALUES (?, ?, ?, ?);", 
                       (stu1_row_id, python_sub_id, "Present", "2026-05-26"))
        cursor.execute("INSERT INTO attendance (student_id, subject_id, status, attendance_date) VALUES (?, ?, ?, ?);", 
                       (stu2_row_id, python_sub_id, "Present", "2026-05-25"))
        cursor.execute("INSERT INTO attendance (student_id, subject_id, status, attendance_date) VALUES (?, ?, ?, ?);", 
                       (stu2_row_id, python_sub_id, "Absent", "2026-05-26"))

        # Marks Seed Data
        cursor.execute("INSERT INTO marks (student_id, subject_id, marks_obtained, max_marks) VALUES (?, ?, ?, ?);", 
                       (stu1_row_id, python_sub_id, 88.5, 100))
        cursor.execute("INSERT INTO marks (student_id, subject_id, marks_obtained, max_marks) VALUES (?, ?, ?, ?);", 
                       (stu2_row_id, python_sub_id, 74.0, 100))

        # Feedback Seed Data (Query board interaction)
        cursor.execute("INSERT INTO feedback (sender_id, message, reply_text, created_at, replied_at) VALUES (?, ?, ?, ?, ?);", 
                       (stu1_user_id, "When is the next local test syllabus for python being active?", 
                        "In the 2nd week of June. Check study plans.", "2026-05-20 10:15:00", "2026-05-21 09:30:00"))
        
        cursor.execute("INSERT INTO feedback (sender_id, message, reply_text, created_at) VALUES (?, ?, ?, ?);", 
                       (stu2_user_id, "Could we get some extra tutorial files for Data Structures recursion local path?", 
                        None, "2026-05-26 14:00:00"))

        # Leaves Seed Data
        cursor.execute("INSERT INTO leave_applications (student_id, message, leave_date, status) VALUES (?, ?, ?, ?);", 
                       (stu1_row_id, "Need leave due to tooth extraction clinic checkup.", "2026-05-28", "Approved"))
        cursor.execute("INSERT INTO leave_applications (student_id, message, leave_date, status) VALUES (?, ?, ?, ?);", 
                       (stu2_row_id, "Family function out of town for two days.", "2026-05-30", "Pending"))
        
        conn.commit()
    conn.close()

# Auth Methods
def authenticate_user(username_or_email, password):
    """Verifies credentials locally against users table and returns user row or None."""
    conn = get_connection()
    cursor = conn.cursor()
    pwd_sha = hash_password(password)
    
    # Authenticate by username or email
    cursor.execute("""
        SELECT * FROM users 
        WHERE (username = ? OR email = ?) AND password_hash = ?
    """, (username_or_email, username_or_email, pwd_sha))
    user = cursor.fetchone()
    conn.close()
    return user

# Helper queries for Dashboard widgets
def get_dashboard_counts():
    """Aggregates local counts for Student, Staff, Course, and Subject entities."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM students")
    students_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM staff")
    staff_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM courses")
    courses_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM subjects")
    subjects_count = c.fetchone()[0]
    
    conn.close()
    return {
        "students": students_count,
        "staff": staff_count,
        "courses": courses_count,
        "subjects": subjects_count
    }

def get_chart_distribution():
    """Aggregates course names and count of students enrolled."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT c.course_name, COUNT(s.id) as student_count 
        FROM courses c
        LEFT JOIN students s ON c.id = s.course_id
        GROUP BY c.id
    """)
    rows = c.fetchall()
    conn.close()
    return {r["course_name"]: r["student_count"] for r in rows}

# Core CRUD: Students
def get_all_students_detailed():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT 
            s.id as student_id,
            u.id as user_id,
            u.first_name, u.last_name, u.username, u.email, u.gender, u.address,
            c.course_name, s.course_id, s.session_start, s.session_end
        FROM students s
        JOIN users u ON s.user_id = u.id
        JOIN courses c ON s.course_id = c.id
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_student(username, password, first_name, last_name, email, gender, address, course_id, session_start, session_end):
    conn = get_connection()
    c = conn.cursor()
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        phash = hash_password(password)
        # Insertion into users
        c.execute("""
            INSERT INTO users (username, password_hash, first_name, last_name, email, user_type, gender, address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, phash, first_name, last_name, email, "Student", gender, address, now_str))
        user_id = c.lastrowid
        # Insertion into students
        c.execute("""
            INSERT INTO students (user_id, course_id, session_start, session_end)
            VALUES (?, ?, ?, ?)
        """, (user_id, course_id, session_start, session_end))
        conn.commit()
        return True, "Student registered successfully."
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return False, f"Database Integrity Error: User/Email already exists. ({str(e)})"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def update_student(student_id, user_id, first_name, last_name, email, gender, address, course_id, session_start, session_end):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            UPDATE users
            SET first_name=?, last_name=?, email=?, gender=?, address=?
            WHERE id=?
        """, (first_name, last_name, email, gender, address, user_id))
        
        c.execute("""
            UPDATE students
            SET course_id=?, session_start=?, session_end=?
            WHERE id=?
        """, (course_id, session_start, session_end, student_id))
        conn.commit()
        return True, "Student updated successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_student(student_id, user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        # Cascade will handle deleting from students thanks to ON DELETE CASCADE
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True, "Student deleted successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# Core CRUD: Courses & Subjects
def get_all_courses():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, course_name FROM courses")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_course(course_name):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO courses (course_name) VALUES (?)", (course_name,))
        conn.commit()
        return True, "Course added."
    except sqlite3.IntegrityError:
        return False, "Course name already exists."
    finally:
        conn.close()

def delete_course(course_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM courses WHERE id=?", (course_id,))
        conn.commit()
        return True, "Course deleted."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_subjects():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.id as subject_id, s.subject_name, s.course_id, s.staff_id, 
               c.course_name, u.first_name || ' ' || u.last_name as staff_name
        FROM subjects s
        JOIN courses c ON s.course_id = c.id
        JOIN staff st ON s.staff_id = st.id
        JOIN users u ON st.user_id = u.id
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_subject(subject_name, course_id, staff_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO subjects (subject_name, course_id, staff_id) VALUES (?, ?, ?)", 
                  (subject_name, course_id, staff_id))
        conn.commit()
        return True, "Subject added successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_subject(subject_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
        conn.commit()
        return True, "Subject deleted."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Staff CRUD & Lookups
def get_all_staff():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.id as staff_id, u.id as user_id, u.first_name, u.last_name, u.email, c.course_name
        FROM staff s
        JOIN users u ON s.user_id = u.id
        JOIN courses c ON s.course_id = c.id
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_staff(username, password, first_name, last_name, email, gender, address, course_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        phash = hash_password(password)
        c.execute("""
            INSERT INTO users (username, password_hash, first_name, last_name, email, user_type, gender, address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, phash, first_name, last_name, email, "Staff", gender, address, now_str))
        user_id = c.lastrowid
        
        c.execute("INSERT INTO staff (user_id, course_id) VALUES (?, ?)", (user_id, course_id))
        conn.commit()
        return True, "Staff/Faculty created successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_staff(staff_id, user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        return True, "Staff/Faculty deleted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Leaves Methods
def get_all_leaves():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT l.id as leave_id, l.message, l.leave_date, l.status,
               u.first_name || ' ' || u.last_name as student_name, c.course_name
        FROM leave_applications l
        JOIN students s ON l.student_id = s.id
        JOIN users u ON s.user_id = u.id
        JOIN courses c ON s.course_id = c.id
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_student_leaves(student_row_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id as leave_id, message, leave_date, status
        FROM leave_applications
        WHERE student_id = ?
    """, (student_row_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def submit_leave(student_row_id, message, leave_date):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO leave_applications (student_id, message, leave_date, status)
            VALUES (?, ?, ?, 'Pending')
        """, (student_row_id, message, leave_date))
        conn.commit()
        return True, "Leave application submitted."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_leave_status(leave_id, status):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE leave_applications SET status=? WHERE id=?", (status, leave_id))
        conn.commit()
        return True, f"Leave application {status.lower()}."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Feedback & Query Board Methods
def get_all_feedbacks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT f.id as feedback_id, f.message, f.reply_text, f.created_at, f.replied_at, 
               u.first_name || ' ' || u.last_name as sender_name, u.user_type
        FROM feedback f
        JOIN users u ON f.sender_id = u.id
        ORDER BY f.created_at DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_student_feedbacks(sender_user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id as feedback_id, message, reply_text, created_at, replied_at
        FROM feedback
        WHERE sender_id = ?
        ORDER BY created_at DESC
    """, (sender_user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def submit_feedback(sender_user_id, message):
    conn = get_connection()
    c = conn.cursor()
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""
            INSERT INTO feedback (sender_id, message, reply_text, created_at)
            VALUES (?, ?, NULL, ?)
        """, (sender_user_id, message, now_str))
        conn.commit()
        return True, "Question posted on offline Query Board."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def reply_feedback(feedback_id, reply_text):
    conn = get_connection()
    c = conn.cursor()
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""
            UPDATE feedback
            SET reply_text=?, replied_at=?
            WHERE id=?
        """, (reply_text, now_str, feedback_id))
        conn.commit()
        return True, "Reply posted key database."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Attendance methods
def get_staff_linked_rows(user_id):
    """Fetches Staff schema ID context and linked course."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, course_id FROM staff WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_students_by_course(course_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.id as student_id, u.first_name || ' ' || u.last_name as student_name
        FROM students s
        JOIN users u ON s.user_id = u.id
        WHERE s.course_id = ?
    """, (course_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_attendance(student_id, subject_id, status, attendance_date):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO attendance (student_id, subject_id, status, attendance_date)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, subject_id, attendance_date) 
            DO UPDATE SET status=excluded.status
        """, (student_id, subject_id, status, attendance_date))
        conn.commit()
        return True, "Attendance saved."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_student_attendance_summary(student_user_id):
    """Detailed summary of attendance for a Student view."""
    conn = get_connection()
    c = conn.cursor()
    # Get student row id first
    c.execute("SELECT id FROM students WHERE user_id = ?", (student_user_id,))
    stu_row = c.fetchone()
    if not stu_row:
        conn.close()
        return []
    
    stu_id = stu_row["id"]
    c.execute("""
        SELECT 
            sub.subject_name,
            COUNT(a.id) as total_classes,
            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present_classes,
            SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) as absent_classes
        FROM subjects sub
        LEFT JOIN attendance a ON sub.id = a.subject_id AND a.student_id = ?
        GROUP BY sub.id
    """, (stu_id,))
    
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Marks management
def get_marks_list(course_id, subject_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.id as student_id, u.first_name || ' ' || u.last_name as student_name,
               m.marks_obtained, m.max_marks
        FROM students s
        JOIN users u ON s.user_id = u.id
        LEFT JOIN marks m ON s.id = m.student_id AND m.subject_id = ?
        WHERE s.course_id = ?
    """, (subject_id, course_id))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_marks(student_id, subject_id, marks_obtained, max_marks):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO marks (student_id, subject_id, marks_obtained, max_marks)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, subject_id)
            DO UPDATE SET marks_obtained=excluded.marks_obtained, max_marks=excluded.max_marks
        """, (student_id, subject_id, marks_obtained, max_marks))
        conn.commit()
        return True, "Marks recorded."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_student_marks(student_user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM students WHERE user_id = ?", (student_user_id,))
    stu_row = c.fetchone()
    if not stu_row:
        conn.close()
        return []
    
    stu_id = stu_row["id"]
    c.execute("""
        SELECT sub.subject_name, m.marks_obtained, m.max_marks
        FROM marks m
        JOIN subjects sub ON m.subject_id = sub.id
        WHERE m.student_id = ?
    """, (stu_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_student_row_id(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM students WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row["id"] if row else None
