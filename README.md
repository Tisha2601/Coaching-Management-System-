# Offline Online Computer Coaching Management System

This is a **COMPLETELY OFFLINE, standalone desktop application** built with Python 3.11+, PyQt6, and SQLite. It operates as a local application that fits a modern desktop workstation and doesn't require any internet connection or web servers to run.

---

## 🛠️ Tech Stack Specifications
- **Language:** Python 3.11+
- **GUI Engine:** `PyQt6` (Highly responsive modern component layout engine)
- **Database Engine:** `SQLite` (Written to local file `coaching_management.db`)
- **Reporting Chart:** Built-in adaptive canvas rendering or `matplotlib` for statistics visualization.

---

## 📂 Project Directory Structure

```text
desktop_app/
├── database.py       # Connects to SQLite, initializes tables, handles local ACID Queries
├── models.py         # Standard Python Dataclass models representing tables
├── main.py           # Core application runtime loop & PyQt6 UI (stacked screens, controls)
└── README.md         # This instructions file
```

---

## 🚀 Setting Up Locally & Running

Follow these simple steps to run the application on your computer:

### 1. Prerequisites
Ensure you have **Python 3.11** or higher. You can verify your version by running:
```bash
python --version
```

### 2. Install Dependencies
Initialize the GUI component library and auxiliary chart library via Python's package manager:
```bash
pip install PyQt6 matplotlib
```
> *Note: If `matplotlib` is not installed, the application will automatically fall back to its internal custom painter canvas to draw analytics, ensuring the app boots seamlessly without any dependency errors!*

### 3. Launch the Application
Run the core file directly from your terminal:
```bash
python main.py
```
Upon execution, the system will:
1. Detect and create a local database file called `coaching_management.db` if it doesn't already exist.
2. Initialize tables matching the target data schema.
3. Automatically seed 1 Admin, 1 Staff member (`Kumar, Rohit`), and 2 Student records with mock attendance/marks logs so the app is instantly ready for exploration!

---

## 🔑 Offline Default Authentication Credentials
The following offline accounts are pre-loaded in the local SQLite table on first launch:

| User Type | Account Username | Password | Full Name / Context |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | System Administrator Panel |
| **Faculty / Staff** | `rohit` | `faculty123` | Rohit Kumar (Python coach in BCA) |
| **Student 1** | `amit` | `student123` | Amit Sharma (BCA stream) |
| **Student 2** | `pooja` | `student123` | Pooja Varma (BCA stream) |

---

## 🖥️ Module Features List

### 1. Admin Master Panel
* **Metric Cards:** Real-time headcount tallies for Students, Faculty, Courses, and Subjects.
* **Analytic Chart:** Aggregations outlining total student placements per stream.
* **Student Directory:** Register new students, update database contact fields, or delete students completely.
* **Course and Subjects grids:** Full list controls to add/edit syllabus subjects or course catalogs.
* **Leave Petitions:** List pending leave applications submitted by students with single-click Approve/Reject actions that update underlying records instantly.

### 2. Faculty / Staff Dashboard
* **Mark Daily Attendance:** Load students linked to designated subjects, select calendar dates, and batch record Present/Absent entries.
* **Manage Exams/Marks Obtained:** View live student grids and enter scores out of custom maximum ranges.
* **Syllabus Manager:** Document absolute coordinates to course syllabus paths or review standard curriculums.
* **Reply Queries Panel:** Answer questions posted by students dynamically.

### 3. Student Portal
* **Attendance Tracker:** Displays attendance metrics and classes attended, with real-time colored warnings for attendance under 75%.
* **Academic Marks Report:** Show scores per subject along with visual performance indicators (Failing / Average / Excellent).
* **Communication Hub Query Board:** Post text questions directly to the database. Instructors answer in real-time.
* **Apply for Study Leaves:** Fill in dates and reason messages, then track whether applications are Approved, Rejected, or Pending.
