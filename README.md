# 🎓 Coaching Management System

> A fully offline, role-based desktop application for managing computer coaching institutes — built with Python, PyQt6, and SQLite.

---

## 📌 Problem Statement

Small and mid-sized coaching institutes in India manage student records, attendance, marks, and fee tracking using manual registers or disconnected spreadsheets. This creates data inconsistency, loss of academic records, and operational inefficiency — especially in areas with limited internet access.

**This project solves that** by providing a completely offline, structured desktop system that any institute can deploy instantly — no server, no internet, no cost.

---

## 🏗️ System Architecture
**Design Pattern:** 3-layer architecture — Presentation (PyQt6 UI) → Business Logic (main.py controllers) → Data Layer (SQLite via database.py)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| GUI Framework | PyQt6 |
| Database | SQLite (local ACID-compliant) |
| Analytics | Matplotlib (with custom fallback canvas renderer) |
| Security | SHA-256 password hashing |
| Architecture | MVC-inspired, offline-first |

---

## 🗄️ Database Schema

The system manages **7 relational tables** with foreign key constraints and CHECK constraints enforced via SQLite PRAGMA:

| Table | Purpose |
|---|---|
| `users` | All system users (Admin, Staff, Student) with hashed passwords |
| `courses` | Course catalog (e.g., BCA, MCA) |
| `subjects` | Subjects linked to courses and assigned faculty |
| `students` | Student enrollment with session dates and course mappings |
| `attendance` | Daily per-subject attendance (Present/Absent) per student |
| `marks` | Exam scores per student per subject with max marks |
| `leave_applications` | Student leave requests with Pending/Approved/Rejected status |
| `feedback` | Student-to-faculty query board with reply tracking |

**Schema highlights:**
- Foreign key integrity enforced across all relational joins
- Role-based access via `user_type CHECK IN ('Admin', 'Staff', 'Student')`
- Auto-seeds realistic mock data on first launch for immediate exploration

---

## 👥 Role-Based Access Control

### 🔴 Admin Panel
- Real-time metric cards: total students, faculty, courses, subjects
- Placement analytics chart (students per stream)
- Full CRUD on Student Directory, Course Catalog, Subject Grid
- Leave petition approval/rejection with one-click database update

### 🟡 Faculty Dashboard
- Batch attendance marking by subject and date
- Enter and update exam marks with custom max-mark ranges
- Syllabus management per course
- Answer student queries in real time

### 🟢 Student Portal
- Attendance tracker with **automated warnings below 75%**
- Academic marks report with performance indicators (Failing / Average / Excellent)
- Leave application submission with live status tracking
- Query board to post questions to faculty

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.11+

### Install dependencies
```bash
pip install PyQt6 matplotlib
### Launch
```bash
cd desktop_app
python main.py