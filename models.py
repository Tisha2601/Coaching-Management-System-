"""
models.py
---------
Contains data structures and standard dataclasses representing the system objects
as specified in the SQLite schema database.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: Optional[int]
    username: str
    password_hash: str
    first_name: str
    last_name: str
    email: str
    user_type: str  # Admin, Staff, Student
    gender: str
    profile_pic_path: Optional[str]
    address: str
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@dataclass
class Course:
    id: Optional[int]
    course_name: str

@dataclass
class Subject:
    id: Optional[int]
    subject_name: str
    course_id: int
    staff_id: int

@dataclass
class Student:
    id: Optional[int]
    user_id: int
    course_id: int
    session_start: str
    session_end: str

@dataclass
class Staff:
    id: Optional[int]
    user_id: int
    course_id: int

@dataclass
class Attendance:
    id: Optional[int]
    student_id: int
    subject_id: int
    status: str  # Present, Absent
    attendance_date: str

@dataclass
class Marks:
    id: Optional[int]
    student_id: int
    subject_id: int
    marks_obtained: float
    max_marks: float

@dataclass
class Feedback:
    id: Optional[int]
    sender_id: int
    message: str
    reply_text: Optional[str] = None
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    replied_at: Optional[str] = None

@dataclass
class LeaveApplication:
    id: Optional[int]
    student_id: int
    message: str
    leave_date: str
    status: str = "Pending"  # Pending, Approved, Rejected
