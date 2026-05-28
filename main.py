"""
main.py
-------
Core entrypoint of the Online Computer Coaching Management System PyQt6 standalone dashboard.
Enforces an offline, local-first workflow backed by SQLite and structured styling.
"""

import sys
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QStackedWidget, 
    QDialog, QFormLayout, QTextEdit, QDateEdit, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen

# Ensure database and models can be imported
import database
import models

# Try importing Matplotlib for analytic chart visualization
try:
    import matplotlib
    matplotlib.use('QtAgg')
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Modern Custom Stylesheet (Dark/Slate Indigo Web-vibe)
APP_STYLESHEET = """
QMainWindow {
    background-color: #f1f5f9;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #1e293b;
}
/* Side Bar Panel */
QFrame#SidebarPanel {
    background-color: #0f172a;
    border: none;
}
QLabel#SidebarTitle {
    color: #f8fafc;
    font-size: 18px;
    font-weight: bold;
    padding: 10px;
    border-bottom: 2px solid #1e293b;
}
QLabel#SidebarSubTitle {
    color: #38bdf8;
    font-size: 11px;
    padding-left: 10px;
    margin-bottom: 20px;
}
QPushButton.SidebarNavButton {
    background-color: transparent;
    color: #cbd5e1;
    border: none;
    text-align: left;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton.SidebarNavButton:hover {
    background-color: #1e293b;
    color: #38bdf8;
    border-left: 4px solid #38bdf8;
}
QPushButton.SidebarNavButton:checked, QPushButton.SidebarNavButton#ActiveNavButton {
    background-color: #1e293b;
    color: #38bdf8;
    border-left: 4px solid #38bdf8;
    font-weight: bold;
}
QLabel#UserCardName {
    color: #f8fafc;
    font-size: 13px;
    font-weight: 600;
}
QLabel#UserCardRole {
    color: #94a3b8;
    font-size: 11px;
}

/* Metric Cards style */
QFrame.MetricCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 15px;
}
QLabel.MetricTitle {
    color: #64748b;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
}
QLabel.MetricValue {
    color: #0f172a;
    font-size: 26px;
    font-weight: bold;
}

/* Data Input Form Fields */
QLineEdit, QComboBox, QTextEdit, QDateEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    color: #0f172a;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 1.5px solid #3b82f6;
}

/* Buttons style */
QPushButton.PrimaryButton {
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton.PrimaryButton:hover {
    background-color: #2563eb;
}
QPushButton.SuccessButton {
    background-color: #10b981;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton.SuccessButton:hover {
    background-color: #059669;
}
QPushButton.DangerButton {
    background-color: #ef4444;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
    font-size: 12px;
}
QPushButton.DangerButton:hover {
    background-color: #dc2626;
}
QPushButton.WarningButton {
    background-color: #f59e0b;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
    font-size: 12px;
}
QPushButton.WarningButton:hover {
    background-color: #d97706;
}

/* Tables */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
}
QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    padding: 8px;
    border: none;
    font-weight: bold;
    font-size: 12px;
    border-bottom: 1px solid #e2e8f0;
}
"""

class CustomDrawChart(QWidget):
    """
    Fallback native QPainter chart if matplotlib is missing.
    Renders simple, clean bar charts representing student headcount.
    """
    def __init__(self, data_dict):
        super().__init__()
        self.data_dict = data_dict or {"BCA": 2, "MCA": 0, "B.Tech": 0}
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(226, 232, 240), 1))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)
        
        # Legend/Title
        painter.setPen(QColor(15, 23, 42))
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        painter.drawText(20, 30, "Course-wise Student Distribution (Local Chart)")
        
        keys = list(self.data_dict.keys())
        values = list(self.data_dict.values())
        max_val = max(values) if values and max(values) > 0 else 1
        
        w = self.width()
        h = self.height()
        
        # Draw Bars
        num_bars = len(keys)
        margin_x = 40
        spacing = 30
        bar_w = int((w - (margin_x * 2) - (spacing * (num_bars - 1))) / num_bars) if num_bars > 0 else 100
        bar_w = max(bar_w, 40)
        
        canvas_h = h - 110 # usable height
        base_y = h - 60
        
        colors = [QColor("#3b82f6"), QColor("#10b981"), QColor("#f59e0b"), QColor("#8b5cf6")]
        
        for i, key in enumerate(keys[:4]):
            val = values[i]
            bar_h = int((val / max_val) * canvas_h)
            x = margin_x + i * (bar_w + spacing)
            y = base_y - bar_h
            
            # Draw bar rectangle
            painter.setBrush(QBrush(colors[i % len(colors)]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, bar_w, bar_h, 4, 4)
            
            # Value tag labels
            painter.setPen(QColor(15, 23, 42))
            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.drawText(x + (bar_w // 2) - 5, y - 8, str(val))
            
            # Category labels
            painter.setPen(QColor(100, 116, 139))
            painter.setFont(QFont("Arial", 9))
            painter.drawText(x, base_y + 20, bar_w, 30, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, key)


class MatplotlibCanvas(FigureCanvas):
    """Integrates Matplotlib plotting backend inside a PyQT widget."""
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()

    def plot_student_distribution(self, data_dict):
        self.axes.clear()
        courses = list(data_dict.keys())
        counts = list(data_dict.values())
        
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
        bars = self.axes.bar(courses, counts, color=colors[:len(courses)], width=0.45)
        
        # Grid and Labels
        self.axes.set_title("Course Placement Headcount", fontsize=11, fontweight='bold', color='#1e293b')
        self.axes.set_ylabel("Enrolled Students", fontsize=9, color='#64748b')
        self.axes.set_xlabel("Locally Offered Courses", fontsize=9, color='#64748b')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_color('#cbd5e1')
        self.axes.spines['bottom'].set_color('#cbd5e1')
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            self.axes.annotate(f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
            
        self.fig.tight_layout()
        self.draw()


class LoginWindow(QWidget):
    """
    Login view prompting local verification.
    Matches standard stacked screen container architecture.
    """
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Coaching System - Secure Login")
        self.resize(800, 500)
        
        # Split layout: Brand side, Input Form side
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Indigo Brand Panel
        brand_panel = QFrame()
        brand_panel.setStyleSheet("background-color: #1e3a8a;")
        brand_layout = QVBoxLayout(brand_panel)
        brand_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        brand_logo = QLabel("🖥️")
        brand_logo.setStyleSheet("font-size: 72px;")
        brand_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        brand_title = QLabel("Computer Coaching\nManagement System")
        brand_title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        brand_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        brand_sub = QLabel("Standlone Offline Console\nSQLite Local Encryption")
        brand_sub.setStyleSheet("color: #93c5fd; font-size: 13px;")
        brand_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        brand_layout.addWidget(brand_logo)
        brand_layout.addWidget(brand_title)
        brand_layout.addWidget(brand_sub)
        
        # 2. Form panel
        form_panel = QWidget()
        form_panel.setStyleSheet("background-color: #ffffff;")
        form_layout = QVBoxLayout(form_panel)
        form_layout.setContentsMargins(60, 40, 60, 40)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        form_title = QLabel("System Sign In")
        form_title.setStyleSheet("color: #0f172a; font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        
        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Local Username or Email")
        self.username_input.setMinimumHeight(40)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Local Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)

        # Credentials Hint box
        hint_box = QLabel(
            "🔑 DEFAULT OFFLINE CREDENTIALS:\n"
            "• Admin: admin / admin123\n"
            "• Staff: rohit / faculty123\n"
            "• Students: amit / student123"
        )
        hint_box.setStyleSheet("color: #475569; background-color: #f1f5f9; padding: 10px; border-radius: 6px; font-size: 11px;")
        hint_box.setWordWrap(True)
        
        # Error text
        self.err_label = QLabel("")
        self.err_label.setStyleSheet("color: #ef4444; font-size: 12px; font-weight: bold;")
        
        # Login Button
        login_btn = QPushButton("Access Control Panel")
        login_btn.setMinimumHeight(45)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        login_btn.clicked.connect(self.run_login)
        self.password_input.returnPressed.connect(self.run_login)
        
        form_layout.addWidget(form_title)
        form_layout.addWidget(QLabel("Local Username/Email"))
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(QLabel("Password"))
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.err_label)
        form_layout.addWidget(login_btn)
        form_layout.addSpacing(20)
        form_layout.addWidget(hint_box)
        
        main_layout.addWidget(brand_panel, 40)
        main_layout.addWidget(form_panel, 60)

    def run_login(self):
        usr_val = self.username_input.text().strip()
        pwd_val = self.password_input.text()
        
        if not usr_val or not pwd_val:
            self.err_label.setText("⚠️ Fields cannot be blank.")
            return
            
        user = database.authenticate_user(usr_val, pwd_val)
        if user:
            self.err_label.setText("")
            self.on_login_success(dict(user))
        else:
            self.err_label.setText("❌ Authentication rejected. Try again.")


class AdminAddStudentDialog(QDialog):
    """Dialogue to add a local Student record."""
    def __init__(self, parent=None, student_data=None):
        super().__init__(parent)
        self.student_data = student_data # If set, is edit mode
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Register Student Record")
        self.setStyleSheet(APP_STYLESHEET)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.email_input = QLineEdit()
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        self.address_input = QLineEdit()
        
        self.course_combo = QComboBox()
        # Populate courses
        self.courses_list = database.get_all_courses()
        for idx, course in enumerate(self.courses_list):
            self.course_combo.addItem(course["course_name"], course["id"])
            
        self.session_start_input = QDateEdit()
        self.session_start_input.setDate(QDate(2025, 1, 1))
        self.session_end_input = QDateEdit()
        self.session_end_input.setDate(QDate(2028, 1, 1))
        
        # If edit mode, load data and disable key credentials fields
        if self.student_data:
            self.first_name_input.setText(self.student_data["first_name"])
            self.last_name_input.setText(self.student_data["last_name"])
            self.username_input.setText(self.student_data["username"])
            self.username_input.setEnabled(False)
            self.password_input.setPlaceholderText("Password locked in edit dashboard")
            self.password_input.setEnabled(False)
            self.email_input.setText(self.student_data["email"])
            self.gender_input.setCurrentText(self.student_data["gender"])
            self.address_input.setText(self.student_data["address"])
            
            c_id = self.student_data["course_id"]
            # match combo list index
            for idx, item in enumerate(self.courses_list):
                if item["id"] == c_id:
                    self.course_combo.setCurrentIndex(idx)
                    break
            
            self.session_start_input.setDate(QDate.fromString(self.student_data["session_start"], "yyyy-MM-dd"))
            self.session_end_input.setDate(QDate.fromString(self.student_data["session_end"], "yyyy-MM-dd"))
        
        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("Username:", self.username_input)
        if not self.student_data:
            form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Gender:", self.gender_input)
        form_layout.addRow("Address Description:", self.address_input)
        form_layout.addRow("Course Linked:", self.course_combo)
        form_layout.addRow("Session Starts:", self.session_start_input)
        form_layout.addRow("Session Ends:", self.session_end_input)
        
        layout.addLayout(form_layout)
        
        # Actions
        btn_box = QHBoxLayout()
        save_btn = QPushButton("Save Entry")
        save_btn.clicked.connect(self.validate_and_save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)
        
    def validate_and_save(self):
        # Gathering
        fn = self.first_name_input.text().strip()
        ln = self.last_name_input.text().strip()
        usr = self.username_input.text().strip()
        email = self.email_input.text().strip()
        gender = self.gender_input.currentText()
        address = self.address_input.text().strip()
        course_id = self.course_combo.currentData()
        start = self.session_start_input.date().toString("yyyy-MM-dd")
        end = self.session_end_input.date().toString("yyyy-MM-dd")
        
        if not fn or not ln or not usr or not email or not address or not course_id:
            QMessageBox.warning(self, "Invalid Inputs", "All fields must be filled correctly.")
            return
            
        if self.student_data:
            # Update mode
            success, msg = database.update_student(
                self.student_data["student_id"], self.student_data["user_id"],
                fn, ln, email, gender, address, course_id, start, end
            )
        else:
            # Create mode
            pwd = self.password_input.text()
            if not pwd:
                QMessageBox.warning(self, "Password Required", "Provide a secure starting password.")
                return
            success, msg = database.create_student(usr, pwd, fn, ln, email, gender, address, course_id, start, end)
            
        if success:
            QMessageBox.information(self, "Database Saved", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Transaction Failed", msg)


class MainWindow(QMainWindow):
    """Main System Container with layout dashboard."""
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Computer Coaching Engine Console v1.0 [OFFLINE]")
        self.resize(1100, 720)
        self.setStyleSheet(APP_STYLESHEET)
        
        # Central horizontal layout splits sidebar and viewport
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==========================================
        # SIDEBAR PANEL
        # ==========================================
        sidebar = QFrame()
        sidebar.setObjectName("SidebarPanel")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 0)
        sidebar_layout.setSpacing(5)
        sidebar.setFixedWidth(230)
        
        title = QLabel("🤖 COACHING SYSTEM")
        title.setObjectName("SidebarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        sub_title = QLabel("Local SQLite Standalone Console")
        sub_title.setObjectName("SidebarSubTitle")
        
        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(sub_title)
        
        # Sidebar User Info Badge
        u_card = QFrame()
        u_card.setStyleSheet("background-color: #1e293b; border-radius: 6px; margin: 10px; padding: 10px;")
        uc_layout = QVBoxLayout(u_card)
        uc_layout.setContentsMargins(5, 5, 5, 5)
        
        un_label = QLabel(f"{self.current_user['first_name']} {self.current_user['last_name']}")
        un_label.setObjectName("UserCardName")
        ur_label = QLabel(f"Role: {self.current_user['user_type'].upper()}")
        ur_label.setObjectName("UserCardRole")
        
        uc_layout.addWidget(un_label)
        uc_layout.addWidget(ur_label)
        sidebar_layout.addWidget(u_card)
        
        # Sidebar Actions Stack buttons depending on login authorization
        self.stacked_views = QStackedWidget()
        self.nav_buttons = []
        
        role = self.current_user["user_type"]
        
        if role == "Admin":
            self.setup_admin_sidebar(sidebar_layout)
        elif role == "Staff":
            self.setup_staff_sidebar(sidebar_layout)
        elif role == "Student":
            self.setup_student_sidebar(sidebar_layout)
            
        sidebar_layout.addStretch()
        
        # Logout Trigger
        logout_btn = QPushButton("🚪 Log Out")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626; color: white; border: none;
                padding: 12px 20px; text-align: left; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background-color: #ef4444; }
        """)
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_views, 1)

    def logout(self):
        # Simple reset back to Login
        self.close()
        # Open login windows in caller
        self.login_window = LoginWindow(self.restart_app_session)
        self.login_window.show()

    def restart_app_session(self, user):
        self.login_window.close()
        self.main_window = MainWindow(user)
        self.main_window.show()

    def setup_admin_sidebar(self, layout):
        # Admin Screens Setup
        btn_dash = QPushButton("📊 Dashboard Analytics")
        btn_stud = QPushButton("🎓 Student Directory")
        btn_courses = QPushButton("📚 Course Catalogs")
        btn_subjects = QPushButton("📐 Subjects Grid")
        btn_leaves = QPushButton("📬 Leave Petitions")
        btn_feedback = QPushButton("💬 Query Forum Board")
        
        widgets_nav = [
            (btn_dash, self.create_admin_dashboard_view()),
            (btn_stud, self.create_admin_student_view()),
            (btn_courses, self.create_admin_courses_view()),
            (btn_subjects, self.create_admin_subjects_view()),
            (btn_leaves, self.create_admin_leaves_view()),
            (btn_feedback, self.create_admin_query_view())
        ]
        
        for idx, (btn, view) in enumerate(widgets_nav):
            btn.setCheckable(True)
            btn.setProperty("style_class", "SidebarNavButton")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: #cbd5e1; border: none;
                    text-align: left; padding: 12px 20px; font-size: 13px;
                }
                QPushButton:hover { background-color: #1e293b; color: #38bdf8; }
                QPushButton:checked { background-color: #1e293b; color: #38bdf8; border-left: 3px solid #38bdf8; font-weight: bold; }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            self.stacked_views.addWidget(view)
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
            # Connection
            btn.clicked.connect(lambda checked, i=idx: self.switch_view_index(i))
            
        # Select first tab by default
        btn_dash.setChecked(True)
        self.switch_view_index(0)

    def setup_staff_sidebar(self, layout):
        btn_att = QPushButton("📝 Mark Attendance")
        btn_marks = QPushButton("🎯 Manage Exam Marks")
        btn_plan = QPushButton("📂 Syllabus & Study Plans")
        btn_queries = QPushButton("💡 Reply Student Queries")
        
        widgets_nav = [
            (btn_att, self.create_staff_attendance_view()),
            (btn_marks, self.create_staff_marks_view()),
            (btn_plan, self.create_staff_syllabus_view()),
            (btn_queries, self.create_staff_query_view())
        ]
        for idx, (btn, view) in enumerate(widgets_nav):
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: #cbd5e1; border: none;
                    text-align: left; padding: 12px 20px; font-size: 13px;
                }
                QPushButton:hover { background-color: #1e293b; color: #38bdf8; }
                QPushButton:checked { background-color: #1e293b; color: #38bdf8; border-left: 3px solid #38bdf8; font-weight: bold; }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.stacked_views.addWidget(view)
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
            btn.clicked.connect(lambda checked, i=idx: self.switch_view_index(i))
            
        btn_att.setChecked(True)
        self.switch_view_index(0)

    def setup_student_sidebar(self, layout):
        btn_att = QPushButton("📉 Attendance Tracker")
        btn_marks = QPushButton("🏆 Academic Marks report")
        btn_plan = QPushButton("📗 Local Syllabus Access")
        btn_leaves = QPushButton("📝 Apply Study Leave")
        btn_queries = QPushButton("💬 Submit Coaching Inquiry")
        
        widgets_nav = [
            (btn_att, self.create_student_attendance_view()),
            (btn_marks, self.create_student_marks_view()),
            (btn_plan, self.create_student_syllabus_view()),
            (btn_leaves, self.create_student_leaves_view()),
            (btn_queries, self.create_student_query_view())
        ]
        for idx, (btn, view) in enumerate(widgets_nav):
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: #cbd5e1; border: none;
                    text-align: left; padding: 12px 20px; font-size: 13px;
                }
                QPushButton:hover { background-color: #1e293b; color: #38bdf8; }
                QPushButton:checked { background-color: #1e293b; color: #38bdf8; border-left: 3px solid #38bdf8; font-weight: bold; }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.stacked_views.addWidget(view)
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
            btn.clicked.connect(lambda checked, i=idx: self.switch_view_index(i))
            
        btn_att.setChecked(True)
        self.switch_view_index(0)

    def switch_view_index(self, target_idx):
        # Deselect others visually
        for i, b in enumerate(self.nav_buttons):
            b.setChecked(i == target_idx)
        self.stacked_views.setCurrentIndex(target_idx)
        
        # Trigger dynamic view updates depending on selection
        # (Allows tables and dashboards to refresh locally)
        role = self.current_user["user_type"]
        if role == "Admin":
            if target_idx == 0: self.refresh_admin_metrics()
            elif target_idx == 1: self.refresh_admin_student_grid()
            elif target_idx == 2: self.refresh_admin_courses_grid()
            elif target_idx == 3: self.refresh_admin_subjects_grid()
            elif target_idx == 4: self.refresh_admin_leaves_grid()
            elif target_idx == 5: self.refresh_admin_query_grid()
        elif role == "Staff":
            if target_idx == 0: self.load_staff_attendance_grid()
            elif target_idx == 1: self.load_staff_marks_grid()
            elif target_idx == 3: self.load_staff_unanswered_queries()
        elif role == "Student":
            if target_idx == 0: self.load_student_attendance_summary()
            elif target_idx == 1: self.load_student_marks_summary()
            elif target_idx == 3: self.load_student_leaves_grid()
            elif target_idx == 4: self.load_student_feedback_grid()

    # =========================================================================
    # VIEW BUILDERS: ADMIN MODULES
    # =========================================================================
    def create_admin_dashboard_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header
        view_title = QLabel("System Dashboard Analytics")
        view_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a;")
        layout.addWidget(view_title)
        
        # Four Metric Cards layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        self.card_students = QFrame()
        self.card_students.setClassName("MetricCard")
        self.card_students.setProperty("class", "MetricCard")
        self.card_students.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 8px;")
        l_stud = QVBoxLayout(self.card_students)
        self.m_stud_title = QLabel("Total Students Enrolled")
        self.m_stud_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        self.m_stud_val = QLabel("0")
        self.m_stud_val.setStyleSheet("color: #3b82f6; font-size: 26px; font-weight: bold;")
        l_stud.addWidget(self.m_stud_title)
        l_stud.addWidget(self.m_stud_val)
        
        self.card_staff = QFrame()
        self.card_staff.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 8px;")
        l_st = QVBoxLayout(self.card_staff)
        self.m_st_title = QLabel("Faculty & Staff")
        self.m_st_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        self.m_st_val = QLabel("0")
        self.m_st_val.setStyleSheet("color: #10b981; font-size: 26px; font-weight: bold;")
        l_st.addWidget(self.m_st_title)
        l_st.addWidget(self.m_st_val)
        
        self.card_courses = QFrame()
        self.card_courses.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 8px;")
        l_c = QVBoxLayout(self.card_courses)
        self.m_c_title = QLabel("Active Courses")
        self.m_c_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        self.m_c_val = QLabel("0")
        self.m_c_val.setStyleSheet("color: #f59e0b; font-size: 26px; font-weight: bold;")
        l_c.addWidget(self.m_c_title)
        l_c.addWidget(self.m_c_val)
        
        self.card_subs = QFrame()
        self.card_subs.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 8px;")
        l_s = QVBoxLayout(self.card_subs)
        self.m_s_title = QLabel("Subjects Catalogue")
        self.m_s_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        self.m_s_val = QLabel("0")
        self.m_s_val.setStyleSheet("color: #8b5cf6; font-size: 26px; font-weight: bold;")
        l_s.addWidget(self.m_s_title)
        l_s.addWidget(self.m_s_val)
        
        cards_layout.addWidget(self.card_students)
        cards_layout.addWidget(self.card_staff)
        cards_layout.addWidget(self.card_courses)
        cards_layout.addWidget(self.card_subs)
        layout.addLayout(cards_layout)
        
        # Analytic Chart Display Container
        self.chart_container = QVBoxLayout()
        layout.addLayout(self.chart_container, 1)
        
        self.refresh_admin_metrics()
        return view

    def refresh_admin_metrics(self):
        counts = database.get_dashboard_counts()
        self.m_stud_val.setText(str(counts["students"]))
        self.m_st_val.setText(str(counts["staff"]))
        self.m_c_val.setText(str(counts["courses"]))
        self.m_s_val.setText(str(counts["subjects"]))
        
        # Redraw chart distributions
        dist = database.get_chart_distribution()
        
        # Wipe old widgets
        for i in reversed(range(self.chart_container.count())): 
            self.chart_container.itemAt(i).widget().setParent(None)
            
        if HAS_MATPLOTLIB:
            canvas = MatplotlibCanvas(self)
            canvas.plot_student_distribution(dist)
            self.chart_container.addWidget(canvas)
        else:
            # Custom drawn widget
            chart_fallback = CustomDrawChart(dist)
            self.chart_container.addWidget(chart_fallback)

    def create_admin_student_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        top_bar = QHBoxLayout()
        title = QLabel("Student Management")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        
        add_btn = QPushButton("⊕ Register Student")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setObjectName("ActiveButton")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981; color: white; border: none; font-weight: 600; padding: 8px 16px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        add_btn.clicked.connect(self.display_add_student_dialog)
        
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(add_btn)
        layout.addLayout(top_bar)
        
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(8)
        self.student_table.setHorizontalHeaderLabels([
            "ID", "Name", "Username", "Email", "Course Placement", "Session Period", "Actions", "User_ID"
        ])
        
        # Hide internal user index
        self.student_table.setColumnHidden(7, True)
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.student_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.student_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.student_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.student_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.student_table)
        self.refresh_admin_student_grid()
        return view

    def refresh_admin_student_grid(self):
        students = database.get_all_students_detailed()
        self.student_table.setRowCount(len(students))
        
        for idx, s in enumerate(students):
            self.student_table.setItem(idx, 0, QTableWidgetItem(str(s["student_id"])))
            self.student_table.setItem(idx, 1, QTableWidgetItem(f"{s['first_name']} {s['last_name']}"))
            self.student_table.setItem(idx, 2, QTableWidgetItem(s["username"]))
            self.student_table.setItem(idx, 3, QTableWidgetItem(s["email"]))
            self.student_table.setItem(idx, 4, QTableWidgetItem(s["course_name"]))
            self.student_table.setItem(idx, 5, QTableWidgetItem(f"{s['session_start']} to {s['session_end']}"))
            
            # Action frame (Edit / Delete buttons side by side)
            action_widget = QWidget()
            aw_layout = QHBoxLayout(action_widget)
            aw_layout.setContentsMargins(4, 2, 4, 2)
            aw_layout.setSpacing(4)
            
            edit_btn = QPushButton("✎ Edit")
            edit_btn.setObjectName("EditTab")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setStyleSheet("""
                QPushButton { background-color: #3b82f6; color: white; border-radius: 4px; padding: 4px 8px; font-size: 11px; }
                QPushButton:hover { background-color: #2563eb; }
            """)
            edit_btn.clicked.connect(lambda checked, s_record=s: self.edit_student_record(s_record))
            
            del_btn = QPushButton("🗑️ Delete")
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setStyleSheet("""
                QPushButton { background-color: #ef4444; color: white; border-radius: 4px; padding: 4px 8px; font-size: 11px; }
                QPushButton:hover { background-color: #dc2626; }
            """)
            del_btn.clicked.connect(lambda checked, s_id=s["student_id"], u_id=s["user_id"]: self.delete_student_record(s_id, u_id))
            
            aw_layout.addWidget(edit_btn)
            aw_layout.addWidget(del_btn)
            self.student_table.setCellWidget(idx, 6, action_widget)
            
            # Store primary keys key editing easily
            self.student_table.setItem(idx, 7, QTableWidgetItem(str(s["user_id"])))

    def display_add_student_dialog(self):
        diag = AdminAddStudentDialog(self)
        if diag.exec() == QDialog.DialogCode.Accepted:
            self.refresh_admin_student_grid()

    def edit_student_record(self, student_record):
        diag = AdminAddStudentDialog(self, student_data=student_record)
        if diag.exec() == QDialog.DialogCode.Accepted:
            self.refresh_admin_student_grid()

    def delete_student_record(self, student_id, user_id):
        reply = QMessageBox.question(
            self, "Confirm File Wipe", 
            "Are you sure you want to completely erase this student, their attendance logs, exam marks, and record entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = database.delete_student(student_id, user_id)
            if success:
                QMessageBox.information(self, "Erased", "Student deleted successfully.")
                self.refresh_admin_student_grid()
            else:
                QMessageBox.critical(self, "Failed Operation", msg)

    def create_admin_courses_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        top_box = QHBoxLayout()
        title = QLabel("Course Directories")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        top_box.addWidget(title)
        top_box.addStretch()
        
        layout.addLayout(top_box)
        
        # Input Form Row
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 10px;")
        ff_layout = QHBoxLayout(form_frame)
        ff_layout.addWidget(QLabel("New Course Name:"))
        self.course_input = QLineEdit()
        self.course_input.setPlaceholderText("e.g. PyML Specialist, BCA, MCA")
        self.course_input.setMinimumWidth(250)
        ff_layout.addWidget(self.course_input)
        
        add_c_btn = QPushButton("⊕ Create Course")
        add_c_btn.setMinimumHeight(35)
        add_c_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_c_btn.setStyleSheet("""
            QPushButton { background-color: #10b981; color: white; border: none; border-radius: 6px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #059669; }
        """)
        add_c_btn.clicked.connect(self.add_new_course)
        ff_layout.addWidget(add_c_btn)
        
        layout.addWidget(form_frame)
        
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(3)
        self.courses_table.setHorizontalHeaderLabels(["ID", "Course Stream Name", "Actions"])
        self.courses_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.courses_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.courses_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.courses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.courses_table)
        self.refresh_admin_courses_grid()
        return view

    def refresh_admin_courses_grid(self):
        courses = database.get_all_courses()
        self.courses_table.setRowCount(len(courses))
        
        for idx, c in enumerate(courses):
            self.courses_table.setItem(idx, 0, QTableWidgetItem(str(c["id"])))
            self.courses_table.setItem(idx, 1, QTableWidgetItem(c["course_name"]))
            
            del_btn = QPushButton("🗑️ Delete")
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setStyleSheet("""
                QPushButton { background-color: #ef4444; color: white; border-radius: 4px; padding: 4px 8px; font-size: 11px; }
                QPushButton:hover { background-color: #dc2626; }
            """)
            del_btn.clicked.connect(lambda checked, c_id=c["id"]: self.delete_course_record(c_id))
            self.courses_table.setCellWidget(idx, 2, del_btn)

    def add_new_course(self):
        cname = self.course_input.text().strip()
        if not cname:
            QMessageBox.warning(self, "Required Inputs", "Provide a course description.")
            return
        success, msg = database.create_course(cname)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.course_input.clear()
            self.refresh_admin_courses_grid()
        else:
            QMessageBox.critical(self, "Fail", msg)

    def delete_course_record(self, course_id):
        reply = QMessageBox.question(
            self, "Confirm Delete", "Remove this course? All associated subjects, staff bindings, and student mappings will be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = database.delete_course(course_id)
            if success:
                self.refresh_admin_courses_grid()
            else:
                QMessageBox.critical(self, "Fail", msg)

    def create_admin_subjects_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Coaching Subjects")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        # Form to add Subject linked to Course and Staff Member
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 12px;")
        ff_layout = QHBoxLayout(form_frame)
        
        self.sub_name_input = QLineEdit()
        self.sub_name_input.setPlaceholderText("Subject name e.g. NumPy basics")
        
        self.sub_course_combo = QComboBox()
        self.sub_staff_combo = QComboBox()
        
        ff_layout.addWidget(QLabel("Name:"))
        ff_layout.addWidget(self.sub_name_input)
        ff_layout.addWidget(QLabel("Course:"))
        ff_layout.addWidget(self.sub_course_combo)
        ff_layout.addWidget(QLabel("Staff Instructor:"))
        ff_layout.addWidget(self.sub_staff_combo)
        
        add_sub_btn = QPushButton("⊕ Add Subject")
        add_sub_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_sub_btn.setStyleSheet("""
            QPushButton { background-color: #10b981; color: white; border-radius: 6px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #059669; }
        """)
        add_sub_btn.clicked.connect(self.add_new_subject)
        ff_layout.addWidget(add_sub_btn)
        
        layout.addWidget(form_frame)
        
        self.subjects_table = QTableWidget()
        self.subjects_table.setColumnCount(5)
        self.subjects_table.setHorizontalHeaderLabels(["ID", "Subject Title", "Related Stream", "Linked Instructor", "Actions"])
        self.subjects_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.subjects_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.subjects_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.subjects_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.subjects_table)
        self.refresh_admin_subjects_grid()
        return view

    def refresh_admin_subjects_grid(self):
        # Refresh combo lists first
        self.sub_course_combo.clear()
        courses = database.get_all_courses()
        for c in courses:
            self.sub_course_combo.addItem(c["course_name"], c["id"])
            
        self.sub_staff_combo.clear()
        staff = database.get_all_staff()
        for s in staff:
            self.sub_staff_combo.addItem(f"{s['first_name']} {s['last_name']}", s["staff_id"])
            
        subjects = database.get_all_subjects()
        self.subjects_table.setRowCount(len(subjects))
        
        for idx, sub in enumerate(subjects):
            self.subjects_table.setItem(idx, 0, QTableWidgetItem(str(sub["subject_id"])))
            self.subjects_table.setItem(idx, 1, QTableWidgetItem(sub["subject_name"]))
            self.subjects_table.setItem(idx, 2, QTableWidgetItem(sub["course_name"]))
            self.subjects_table.setItem(idx, 3, QTableWidgetItem(sub["staff_name"]))
            
            del_btn = QPushButton("🗑️ Delete")
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setStyleSheet("""
                QPushButton { background-color: #ef4444; color: white; border-radius: 4px; padding: 4px 8px; font-size: 11px; }
                QPushButton:hover { background-color: #dc2626; }
            """)
            del_btn.clicked.connect(lambda checked, s_id=sub["subject_id"]: self.delete_subject_record(s_id))
            self.subjects_table.setCellWidget(idx, 4, del_btn)

    def add_new_subject(self):
        sname = self.sub_name_input.text().strip()
        cid = self.sub_course_combo.currentData()
        sid = self.sub_staff_combo.currentData()
        
        if not sname or not cid or not sid:
            QMessageBox.warning(self, "Invalid Parameters", "Complete subject details first.")
            return
        success, msg = database.create_subject(sname, cid, sid)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.sub_name_input.clear()
            self.refresh_admin_subjects_grid()
        else:
            QMessageBox.critical(self, "Fail", msg)

    def delete_subject_record(self, subject_id):
        reply = QMessageBox.question(self, "Confirm Delete", "Remove this subject catalog entity?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = database.delete_subject(subject_id)
            if success:
                self.refresh_admin_subjects_grid()
            else:
                QMessageBox.critical(self, "Fail", msg)

    def create_admin_leaves_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Leave Applications Control Panel")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        self.admin_leaves_table = QTableWidget()
        self.admin_leaves_table.setColumnCount(6)
        self.admin_leaves_table.setHorizontalHeaderLabels(["ID", "Student", "Course", "Leave Date", "Reason / Message", "Actions"])
        self.admin_leaves_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.admin_leaves_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.admin_leaves_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.admin_leaves_table)
        self.refresh_admin_leaves_grid()
        return view

    def refresh_admin_leaves_grid(self):
        leaves = database.get_all_leaves()
        self.admin_leaves_table.setRowCount(len(leaves))
        
        for idx, l in enumerate(leaves):
            self.admin_leaves_table.setItem(idx, 0, QTableWidgetItem(str(l["leave_id"])))
            self.admin_leaves_table.setItem(idx, 1, QTableWidgetItem(l["student_name"]))
            self.admin_leaves_table.setItem(idx, 2, QTableWidgetItem(l["course_name"]))
            self.admin_leaves_table.setItem(idx, 3, QTableWidgetItem(l["leave_date"]))
            self.admin_leaves_table.setItem(idx, 4, QTableWidgetItem(l["message"]))
            
            status = l["status"]
            if status == "Pending":
                action_widget = QWidget()
                aw_layout = QHBoxLayout(action_widget)
                aw_layout.setContentsMargins(4, 2, 4, 2)
                aw_layout.setSpacing(4)
                
                app_btn = QPushButton("✓ Approve")
                app_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                app_btn.setStyleSheet("""
                    QPushButton { background-color: #10b981; color: white; border-radius: 4px; padding: 4px 8px; font-size: 11px; }
                    QPushButton:hover { background-color: #059669; }
                """)
                app_btn.clicked.connect(lambda checked, l_id=l["leave_id"]: self.approve_leave(l_id))
                
                rej_btn = QPushButton("✗ Reject")
                rej_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                rej_btn.setStyleSheet("""
                    QPushButton { background-color: #ef4444; color: white; border-radius: 4px; padding: 4px 8px; font-size: 11px; }
                    QPushButton:hover { background-color: #dc2626; }
                """)
                rej_btn.clicked.connect(lambda checked, l_id=l["leave_id"]: self.reject_leave(l_id))
                
                aw_layout.addWidget(app_btn)
                aw_layout.addWidget(rej_btn)
                self.admin_leaves_table.setCellWidget(idx, 5, action_widget)
            else:
                lbl = QLabel(status.upper())
                # Status-based styling
                color = "#059669" if status == "Approved" else "#dc2626"
                lbl.setStyleSheet(f"color: {color}; font-weight: bold; margin-left: 10px;")
                self.admin_leaves_table.setCellWidget(idx, 5, lbl)

    def approve_leave(self, leave_id):
        database.update_leave_status(leave_id, "Approved")
        self.refresh_admin_leaves_grid()

    def reject_leave(self, leave_id):
        database.update_leave_status(leave_id, "Rejected")
        self.refresh_admin_leaves_grid()

    def create_admin_query_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Query Forum Board (Admin Monitor)")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        self.admin_queries_table = QTableWidget()
        self.admin_queries_table.setColumnCount(5)
        self.admin_queries_table.setHorizontalHeaderLabels(["ID", "Sender", "Query Description", "Faculty Response", "Created On"])
        self.admin_queries_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.admin_queries_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.admin_queries_table)
        self.refresh_admin_query_grid()
        return view

    def refresh_admin_query_grid(self):
        feedbacks = database.get_all_feedbacks()
        self.admin_queries_table.setRowCount(len(feedbacks))
        
        for idx, f in enumerate(feedbacks):
            self.admin_queries_table.setItem(idx, 0, QTableWidgetItem(str(f["feedback_id"])))
            self.admin_queries_table.setItem(idx, 1, QTableWidgetItem(f"{f['sender_name']} ({f['user_type']})"))
            self.admin_queries_table.setItem(idx, 2, QTableWidgetItem(f["message"]))
            reply = f["reply_text"] or "(Pending Staff Reply)"
            self.admin_queries_table.setItem(idx, 3, QTableWidgetItem(reply))
            self.admin_queries_table.setItem(idx, 4, QTableWidgetItem(f["created_at"]))


    # =========================================================================
    # VIEW BUILDERS: FACULTY/STAFF MODULES
    # =========================================================================
    def create_staff_attendance_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Mark Daily Attendance")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        # Select target filters
        filter_box = QHBoxLayout()
        self.att_sub_combo = QComboBox()
        self.att_date_edit = QDateEdit()
        self.att_date_edit.setCalendarPopup(True)
        self.att_date_edit.setDate(QDate.currentDate())
        
        filter_box.addWidget(QLabel("Select Lecture Subject:"))
        filter_box.addWidget(self.att_sub_combo)
        filter_box.addWidget(QLabel("Lecture Date:"))
        filter_box.addWidget(self.att_date_edit)
        
        fetch_btn = QPushButton("✏️ Update Log Sheet")
        fetch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fetch_btn.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; border-radius: 6px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        fetch_btn.clicked.connect(self.load_staff_attendance_grid)
        filter_box.addWidget(fetch_btn)
        filter_box.addStretch()
        
        layout.addLayout(filter_box)
        
        # Grid Sheet
        self.att_table = QTableWidget()
        self.att_table.setColumnCount(3)
        self.att_table.setHorizontalHeaderLabels(["Student ID", "Full Name", "Attendance Status"])
        self.att_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.att_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.att_table)
        
        save_btn = QPushButton("💾 Save Sheet to SQLite Database")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton { background-color: #10b981; color: white; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background-color: #059669; }
        """)
        save_btn.clicked.connect(self.save_staff_attendance_log)
        layout.addWidget(save_btn)
        
        # Populate linked subject list
        self.populate_staff_subjects(self.att_sub_combo)
        self.load_staff_attendance_grid()
        return view

    def populate_staff_subjects(self, combo):
        combo.clear()
        linked_staff_row = database.get_staff_linked_rows(self.current_user["id"])
        if not linked_staff_row:
             return
        subjects = database.get_all_subjects()
        # Filter subjects taught by this staff member
        for sub in subjects:
            if sub["staff_id"] == linked_staff_row["id"]:
                combo.addItem(f"{sub['subject_name']} ({sub['course_name']})", sub["subject_id"])

    def load_staff_attendance_grid(self):
        sub_id = self.att_sub_combo.currentData()
        if not sub_id:
            return
            
        # Subject info -> course info
        con = database.get_connection()
        cur = con.cursor()
        cur.execute("SELECT course_id FROM subjects WHERE id=?", (sub_id,))
        subject_record = cur.fetchone()
        con.close()
        
        if not subject_record:
            return
            
        course_id = subject_record["course_id"]
        students = database.get_students_by_course(course_id)
        
        self.att_table.setRowCount(len(students))
        
        # Get existing attendance entries for date to load them
        date_str = self.att_date_edit.date().toString("yyyy-MM-dd")
        con = database.get_connection()
        cur = con.cursor()
        cur.execute("SELECT student_id, status FROM attendance WHERE subject_id=? AND attendance_date=?", (sub_id, date_str))
        existing = {r["student_id"]: r["status"] for r in cur.fetchall()}
        con.close()
        
        for idx, student in enumerate(students):
            stu_id_val = student["student_id"]
            self.att_table.setItem(idx, 0, QTableWidgetItem(str(stu_id_val)))
            self.att_table.setItem(idx, 1, QTableWidgetItem(student["student_name"]))
            
            combo_status = QComboBox()
            combo_status.addItems(["Present", "Absent"])
            if stu_id_val in existing:
                combo_status.setCurrentText(existing[stu_id_val])
            self.att_table.setCellWidget(idx, 2, combo_status)

    def save_staff_attendance_log(self):
        sub_id = self.att_sub_combo.currentData()
        date_str = self.att_date_edit.date().toString("yyyy-MM-dd")
        if not sub_id:
            return
            
        row_count = self.att_table.rowCount()
        errors = False
        for r in range(row_count):
            stu_id = int(self.att_table.item(r, 0).text())
            combo = self.att_table.cellWidget(r, 2)
            status = combo.currentText()
            
            success, msg = database.mark_attendance(stu_id, sub_id, status, date_str)
            if not success:
                errors = True
                
        if not errors:
            QMessageBox.information(self, "Success", f"Attendance logged successfully for {date_str}.")
        else:
            QMessageBox.critical(self, "Failure", "Some student records failed write validation.")

    def create_staff_marks_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Academic Student Marks Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        # Subject selector
        tb = QHBoxLayout()
        self.marks_sub_combo = QComboBox()
        self.populate_staff_subjects(self.marks_sub_combo)
        
        tb.addWidget(QLabel("Select Subject Stream:"))
        tb.addWidget(self.marks_sub_combo)
        
        load_btn = QPushButton("🔍 Load List")
        load_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        load_btn.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; border-radius: 6px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        load_btn.clicked.connect(self.load_staff_marks_grid)
        tb.addWidget(load_btn)
        tb.addStretch()
        
        layout.addLayout(tb)
        
        # Dynamic Grid
        self.marks_table = QTableWidget()
        self.marks_table.setColumnCount(4)
        self.marks_table.setHorizontalHeaderLabels(["Student ID", "Full Name", "Marks Obtained", "Max Marks"])
        self.marks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.marks_table)
        
        save_btn = QPushButton("💾 Write Exam Marks to Database Table")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton { background-color: #10b981; color: white; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background-color: #059669; }
        """)
        save_btn.clicked.connect(self.save_staff_marks_log)
        layout.addWidget(save_btn)
        
        self.load_staff_marks_grid()
        return view

    def load_staff_marks_grid(self):
        sub_id = self.marks_sub_combo.currentData()
        if not sub_id:
            return
            
        # Get course id for subject
        con = database.get_connection()
        cur = con.cursor()
        cur.execute("SELECT course_id FROM subjects WHERE id=?", (sub_id,))
        course_id = cur.fetchone()["course_id"]
        con.close()
        
        marks_rows = database.get_marks_list(course_id, sub_id)
        self.marks_table.setRowCount(len(marks_rows))
        
        for idx, m in enumerate(marks_rows):
            self.marks_table.setItem(idx, 0, QTableWidgetItem(str(m["student_id"])))
            self.marks_table.setItem(idx, 1, QTableWidgetItem(m["student_name"]))
            
            # Form Inputs
            obt_inp = QLineEdit(str(m["marks_obtained"] or "0.0"))
            max_inp = QLineEdit(str(m["max_marks"] or "100.0"))
            
            self.marks_table.setCellWidget(idx, 2, obt_inp)
            self.marks_table.setCellWidget(idx, 3, max_inp)

    def save_staff_marks_log(self):
        sub_id = self.marks_sub_combo.currentData()
        if not sub_id:
            return
            
        row_count = self.marks_table.rowCount()
        errors = False
        for r in range(row_count):
            stu_id = int(self.marks_table.item(r, 0).text())
            obt = float(self.marks_table.cellWidget(r, 2).text().strip() or 0.0)
            mx = float(self.marks_table.cellWidget(r, 3).text().strip() or 100.0)
            
            if obt > mx:
                QMessageBox.warning(self, "Invalid Ranges", "Marks obtained cannot exceed max marks bounds.")
                return
                
            success, msg = database.save_marks(stu_id, sub_id, obt, mx)
            if not success:
                errors = True
                
        if not errors:
            QMessageBox.information(self, "Database Updated", "Exam results catalog table updated successfully.")
        else:
            QMessageBox.critical(self, "Integrity Error", "Some entries failed numeric constraints checks.")

    def create_staff_syllabus_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        title = QLabel("Syllabus & Lesson Plans")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        # Local PDF / File Upload registration mock frame
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 20px; border: 1.5px dashed #cbd5e1;")
        if_layout = QVBoxLayout(info_frame)
        if_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon = QLabel("📂")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        desc = QLabel("Offline Lecture Syllabus Manager\nMap localized course syllabus folders or text schemes:")
        desc.setStyleSheet("color: #475569; text-align: center; font-size: 14px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        path_box = QHBoxLayout()
        self.local_path_input = QLineEdit()
        self.local_path_input.setPlaceholderText("Paste offline absolute file coordinates or local description")
        self.local_path_input.setText("C:/CoachingApp/StudyMaterial/python_bca_syllabus.txt")
        self.local_register_subject = QComboBox()
        self.populate_staff_subjects(self.local_register_subject)
        
        path_box.addWidget(self.local_register_subject)
        path_box.addWidget(self.local_path_input)
        
        reg_btn = QPushButton("Register Resource")
        reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_btn.setStyleSheet("QPushButton { background-color: #3b82f6; color: white; padding: 8px 12px; border-radius: 6px; }")
        reg_btn.clicked.connect(lambda: QMessageBox.information(self, "Offline Path Saved", "Mock link reference point captured in SQLite database config."))
        path_box.addWidget(reg_btn)
        
        if_layout.addWidget(icon)
        if_layout.addWidget(desc)
        if_layout.addLayout(path_box)
        
        layout.addWidget(info_frame)
        
        # Static text listing current scheme (For BCA-Python)
        syllabus_view = QTextEdit()
        syllabus_view.setReadOnly(True)
        syllabus_view.setText(
            "=== BCA COURSE SYLLABUS: PYTHON OBJECTIVES ===\n"
            "Unit I: Syntax & Data Collections (Lists, Dicts, Tuples)\n"
            "Unit II: Control Structures & Iterative Loops\n"
            "Unit III: OOP structures, Functions, Class Inheritance patterns\n"
            "Unit IV: File I/O operations & local SQLite operations with sqlite3\n"
            "Unit V: Modern Standalone desktop controls using PyQt6 framework\n\n"
            "Status: ACTIVE [Modified date: 2026-05-27]"
        )
        layout.addWidget(syllabus_view)
        return view

    def create_staff_query_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Student Query Reply Hub [Communication Board]")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        self.staff_query_table = QTableWidget()
        self.staff_query_table.setColumnCount(4)
        self.staff_query_table.setHorizontalHeaderLabels(["ID", "Sender / Date", "Syllabus Question", "Compose Reply"])
        self.staff_query_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.staff_query_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.staff_query_table)
        
        self.load_staff_unanswered_queries()
        return view

    def load_staff_unanswered_queries(self):
        # Fetch feedbacks
        feedbacks = database.get_all_feedbacks()
        self.staff_query_table.setRowCount(len(feedbacks))
        
        for idx, f in enumerate(feedbacks):
            self.staff_query_table.setItem(idx, 0, QTableWidgetItem(str(f["feedback_id"])))
            self.staff_query_table.setItem(idx, 1, QTableWidgetItem(f"{f['sender_name']}\n{f['created_at']}"))
            self.staff_query_table.setItem(idx, 2, QTableWidgetItem(f["message"]))
            
            reply_val = f["reply_text"]
            if not reply_val:
                action_frame = QWidget()
                af_layout = QHBoxLayout(action_frame)
                af_layout.setContentsMargins(0, 0, 0, 0)
                
                txt = QLineEdit()
                txt.setPlaceholderText("Type localized answer here...")
                
                reply_btn = QPushButton("Submit Answer")
                reply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                reply_btn.setStyleSheet("""
                    QPushButton { background-color: #10b981; color: white; border-radius: 4px; padding: 4px 8px; font-size: 11px; }
                    QPushButton:hover { background-color: #059669; }
                """)
                reply_btn.clicked.connect(lambda checked, f_id=f["feedback_id"], t_box=txt: self.submit_query_response(f_id, t_box))
                
                af_layout.addWidget(txt)
                af_layout.addWidget(reply_btn)
                self.staff_query_table.setCellWidget(idx, 3, action_frame)
            else:
                self.staff_query_table.setItem(idx, 3, QTableWidgetItem(f"REPLIED: {reply_val}"))

    def submit_query_response(self, feedback_id, t_box):
        ans = t_box.text().strip()
        if not ans:
            QMessageBox.warning(self, "Empty Value", "Provide a detailed query answer.")
            return
        success, msg = database.reply_feedback(feedback_id, ans)
        if success:
            QMessageBox.information(self, "Success", "Reply committed to database.")
            self.load_staff_unanswered_queries()
        else:
            QMessageBox.critical(self, "Fail", msg)


    # =========================================================================
    # VIEW BUILDERS: STUDENT PORTAL MODULES
    # =========================================================================
    def create_student_attendance_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Personal Attendance Metrics")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        self.student_att_table = QTableWidget()
        self.student_att_table.setColumnCount(5)
        self.student_att_table.setHorizontalHeaderLabels([
            "Subject Name", "Total Lectures", "Attended Classes", "Absent Count", "Percentage Present"
        ])
        self.student_att_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.student_att_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.student_att_table)
        self.load_student_attendance_summary()
        return view

    def load_student_attendance_summary(self):
        summary = database.get_student_attendance_summary(self.current_user["id"])
        self.student_att_table.setRowCount(len(summary))
        
        for idx, row in enumerate(summary):
            total = row["total_classes"] or 0
            present = row["present_classes"] or 0
            absent = row["absent_classes"] or 0
            
            p_percent = f"{(present / total * 100):.1f}%" if total > 0 else "N/A"
            
            self.student_att_table.setItem(idx, 0, QTableWidgetItem(row["subject_name"]))
            self.student_att_table.setItem(idx, 1, QTableWidgetItem(str(total)))
            self.student_att_table.setItem(idx, 2, QTableWidgetItem(str(present)))
            self.student_att_table.setItem(idx, 3, QTableWidgetItem(str(absent)))
            
            pct_item = QTableWidgetItem(p_percent)
            if total > 0:
                pct = present / total
                if pct < 0.75:
                    pct_item.setForeground(QColor("#ef4444")) # Low attendance red
                    pct_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
                else:
                    pct_item.setForeground(QColor("#10b981")) # Good attendance green
            self.student_att_table.setItem(idx, 4, pct_item)

    def create_student_marks_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Academic Record sheets")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        self.student_marks_table = QTableWidget()
        self.student_marks_table.setColumnCount(4)
        self.student_marks_table.setHorizontalHeaderLabels(["Subject Name", "Marks Obtained", "Maximum Marks", "Performance Metric"])
        self.student_marks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.student_marks_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.student_marks_table)
        self.load_student_marks_summary()
        return view

    def load_student_marks_summary(self):
        marks = database.get_student_marks(self.current_user["id"])
        self.student_marks_table.setRowCount(len(marks))
        
        for idx, m in enumerate(marks):
            self.student_marks_table.setItem(idx, 0, QTableWidgetItem(m["subject_name"]))
            self.student_marks_table.setItem(idx, 1, QTableWidgetItem(str(m["marks_obtained"])))
            self.student_marks_table.setItem(idx, 2, QTableWidgetItem(str(m["max_marks"])))
            
            p_percent = (m["marks_obtained"] / m["max_marks"]) if m["max_marks"] > 0 else 0
            perc_str = f"{p_percent * 100:.1f}%"
            
            perf_item = QTableWidgetItem(perc_str)
            if p_percent >= 0.85:
                perf_item.setText(f"{perc_str} (EXCELLENT)")
                perf_item.setForeground(QColor("#10b981"))
            elif p_percent >= 0.60:
                perf_item.setText(f"{perc_str} (AVERAGE)")
                perf_item.setForeground(QColor("#f59e0b"))
            else:
                perf_item.setText(f"{perc_str} (FAILING)")
                perf_item.setForeground(QColor("#ef4444"))
                
            self.student_marks_table.setItem(idx, 3, perf_item)

    def create_student_syllabus_view(self):
        # Read-only access to localized plans
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Study Resource directories")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        syllabus_box = QTextEdit()
        syllabus_box.setReadOnly(True)
        syllabus_box.setText(
            "=== LOCAL OFFLINE COACHING STUDY DIRECTORY ===\n"
            "• Course Stream: BCA Segment\n"
            "• Syllabus Repository: Shared Folder (C:/CoachingApp/StudyMaterial)\n"
            "• Recommended Reference Reading: 'Intro to Python Object Patterns' (Local Copy PDF)\n\n"
            "To download and read local copies offline, use the local shared directories on building workstation terminals."
        )
        layout.addWidget(syllabus_box)
        return view

    def create_student_leaves_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Apply for Study Leaves")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        # New Leave Application row form
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 12px;")
        ff_layout = QHBoxLayout(form_frame)
        
        self.leave_message_input = QLineEdit()
        self.leave_message_input.setPlaceholderText("State reason for leave application...")
        
        self.leave_date_input = QDateEdit()
        self.leave_date_input.setCalendarPopup(True)
        self.leave_date_input.setDate(QDate.currentDate())
        
        ff_layout.addWidget(QLabel("Date Requested:"))
        ff_layout.addWidget(self.leave_date_input)
        ff_layout.addWidget(QLabel("Reason Message:"))
        ff_layout.addWidget(self.leave_message_input, 1)
        
        submit_btn = QPushButton("Submit Petition")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; border-radius: 6px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        submit_btn.clicked.connect(self.submit_student_leave_recs)
        ff_layout.addWidget(submit_btn)
        
        layout.addWidget(form_frame)
        
        # Grid of past leaves
        self.student_leaves_table = QTableWidget()
        self.student_leaves_table.setColumnCount(3)
        self.student_leaves_table.setHorizontalHeaderLabels(["Leave Date", "Reason", "Application Status"])
        self.student_leaves_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.student_leaves_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.student_leaves_table)
        self.load_student_leaves_grid()
        return view

    def load_student_leaves_grid(self):
        stu_id = database.get_student_row_id(self.current_user["id"])
        if not stu_id:
            return
        leaves = database.get_student_leaves(stu_id)
        self.student_leaves_table.setRowCount(len(leaves))
        
        for idx, l in enumerate(leaves):
            self.student_leaves_table.setItem(idx, 0, QTableWidgetItem(l["leave_date"]))
            self.student_leaves_table.setItem(idx, 1, QTableWidgetItem(l["message"]))
            
            st_item = QTableWidgetItem(l["status"].upper())
            if l["status"] == "Approved":
                st_item.setForeground(QColor("#10b981"))
            elif l["status"] == "Rejected":
                st_item.setForeground(QColor("#ef4444"))
            else:
                st_item.setForeground(QColor("#f59e0b"))
            self.student_leaves_table.setItem(idx, 2, st_item)

    def submit_student_leave_recs(self):
        stu_id = database.get_student_row_id(self.current_user["id"])
        msg = self.leave_message_input.text().strip()
        date_str = self.leave_date_input.date().toString("yyyy-MM-dd")
        
        if not msg:
            QMessageBox.warning(self, "Blank Reason", "A concise description must accompany your leave request.")
            return
            
        success, res = database.submit_leave(stu_id, msg, date_str)
        if success:
            QMessageBox.information(self, "Success", "Leave application submitted locally to database.")
            self.leave_message_input.clear()
            self.load_student_leaves_grid()
        else:
            QMessageBox.critical(self, "Fail", res)

    def create_student_query_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Interactive Query Board (Post Offline Questions)")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)
        
        # Ask question row
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 12px;")
        ff_layout = QHBoxLayout(form_frame)
        
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Type coaching inquiry, course query, or syllabus question here...")
        
        ask_btn = QPushButton("Post Question")
        ask_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ask_btn.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; border-radius: 6px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        ask_btn.clicked.connect(self.submit_student_query_recs)
        
        ff_layout.addWidget(QLabel("New Query:"))
        ff_layout.addWidget(self.question_input, 1)
        ff_layout.addWidget(ask_btn)
        
        layout.addWidget(form_frame)
        
        # History board
        self.student_queries_table = QTableWidget()
        self.student_queries_table.setColumnCount(4)
        self.student_queries_table.setHorizontalHeaderLabels(["Posted Date", "Your Question", "Instructor Answer", "Replied At"])
        self.student_queries_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.student_queries_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.student_queries_table)
        self.load_student_feedback_grid()
        return view

    def load_student_feedback_grid(self):
        queries = database.get_student_feedbacks(self.current_user["id"])
        self.student_queries_table.setRowCount(len(queries))
        
        for idx, q in enumerate(queries):
            self.student_queries_table.setItem(idx, 0, QTableWidgetItem(q["created_at"]))
            self.student_queries_table.setItem(idx, 1, QTableWidgetItem(q["message"]))
            
            ans = q["reply_text"] or "(Pending Faculty response on Board)"
            ans_item = QTableWidgetItem(ans)
            if not q["reply_text"]:
                ans_item.setForeground(QColor("#f59e0b"))
            else:
                ans_item.setForeground(QColor("#10b981"))
            self.student_queries_table.setItem(idx, 2, ans_item)
            self.student_queries_table.setItem(idx, 3, QTableWidgetItem(q["replied_at"] or "N/A"))

    def submit_student_query_recs(self):
        msg = self.question_input.text().strip()
        if not msg:
            QMessageBox.warning(self, "Empty field", "Type a question before posting.")
            return
        success, res = database.submit_feedback(self.current_user["id"], msg)
        if success:
            QMessageBox.information(self, "Posted", "Question posted to the localized Query Board successfully.")
            self.question_input.clear()
            self.load_student_feedback_grid()
        else:
            QMessageBox.critical(self, "Fail", res)


if __name__ == '__main__':
    # Initialize the local database automatically before starting GUI loop.
    database.initialize_db()
    
    app = QApplication(sys.argv)
    
    # Establish a default fallback session start layout -> Login Window
    def start_main_application(authorized_user):
        login_wrapper.close()
        global main_view
        main_view = MainWindow(authorized_user)
        main_view.show()
        
    login_wrapper = LoginWindow(start_main_application)
    login_wrapper.show()
    
    sys.exit(app.exec())
