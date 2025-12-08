from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox, QHBoxLayout
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
import time


class LoginPage(QWidget):
    def __init__(self, db_conn, on_admin_login, on_captain_login):
        super().__init__()
        self.db_conn = db_conn
        self.on_admin_login = on_admin_login
        self.on_captain_login = on_captain_login

        self.setWindowTitle("清华大学乒乓球联赛管理系统")
        self.setFixedSize(450, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Segoe UI, Arial, sans-serif;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                margin: 5px 0px;
            }
            QLineEdit:focus {
                border-color: #e41e2b;
                background-color: #fff9f9;
            }
            QPushButton {
                background-color: #e41e2b;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                margin: 10px 0px;
            }
            QPushButton:hover {
                background-color: #c41623;
            }
            QPushButton:pressed {
                background-color: #a3121d;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLabel#title {
                color: #e41e2b;
                margin: 15px 0px;
            }
            QCheckBox {
                color: #666;
                font-size: 12px;
                font-family: Segoe UI, Arial, sans-serif;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #ccc;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #e41e2b;
                background-color: #e41e2b;
                border-radius: 3px;
            }
        """)
        self.is_loading = False

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo with better styling
        self.logo = QLabel()
        # Try to load logo, fallback to text if not found
        try:
            pixmap = QPixmap("logo.png")  # Replace with your logo
            if pixmap.isNull():
                raise FileNotFoundError
            pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            self.logo.setPixmap(pixmap)
        except:
            # Fallback: Create a styled text logo
            self.logo.setText("🏓")
            self.logo.setStyleSheet("font-size: 60px;")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo)

        # Title with universal fonts
        title = QLabel("清华大学乒乓球联赛管理系统")
        title.setObjectName("title")
        # Font fallback: Microsoft YaHei (Chinese) -> Arial -> sans-serif
        title_font = QFont()
        title_font.setFamily("Microsoft YaHei, SimHei, Arial")
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle with universal fonts
        subtitle = QLabel("Table Tennis Competition Management System")
        subtitle_font = QFont()
        subtitle_font.setFamily("Segoe UI, Arial, sans-serif")
        subtitle_font.setPointSize(10)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #666; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Add some spacing
        layout.addSpacing(20)

        # Username input with icon placeholder
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("👤 Username (Admin: 'admin' | Captain: Student ID)")
        self.username_input.setFixedHeight(45)

        # Set font for input fields
        input_font = QFont()
        input_font.setFamily("Segoe UI, Arial, sans-serif")
        input_font.setPointSize(13)
        self.username_input.setFont(input_font)

        layout.addWidget(self.username_input)

        # Password input with icon placeholder
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("🔒 Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.setFont(input_font)
        layout.addWidget(self.password_input)

        # Login button with better styling
        self.login_btn = QPushButton("Login")
        self.login_btn.setFixedHeight(55)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.login)

        # Set button font
        button_font = QFont()
        button_font.setFamily("Segoe UI, Arial, sans-serif")
        button_font.setPointSize(14)
        button_font.setWeight(QFont.Weight.Bold)
        self.login_btn.setFont(button_font)

        layout.addWidget(self.login_btn)

        # Footer text
        footer = QLabel("Tsinghua University Sports Department © 2024")
        footer_font = QFont()
        footer_font.setFamily("Segoe UI, Arial, sans-serif")
        footer_font.setPointSize(9)
        footer.setFont(footer_font)
        footer.setStyleSheet("color: #999; margin-top: 20px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

        self.setLayout(layout)

        # Set focus and enter key behavior
        self.username_input.setFocus()
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.login)

        # Admin credentials
        self.admin_credentials = {"admin": "admin"}

    def login(self):
        if self.is_loading:
            return

        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password")
            return

        # Show loading state
        self.is_loading = True
        self.login_btn.setText("Logging in...")
        self.login_btn.setEnabled(False)

        # Simulate network delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(800, lambda: self.process_login(username, password))

    def process_login(self, username, password):
        # Check if admin login
        if username in self.admin_credentials and self.admin_credentials[username] == password:
            self.login_btn.setText("Success!")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, lambda: self.finalize_admin_login(username))
            return

        # Check if captain login
        captain_info = self.verify_captain_login(username, password)
        if captain_info:
            self.login_btn.setText("Success!")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, lambda: self.finalize_captain_login(captain_info))
            return

        # Login failed
        QMessageBox.warning(self, "Login Failed", "Invalid username or password")
        self.reset_login_button()

    def verify_captain_login(self, student_id, password):
        """Verify captain login credentials"""
        # For simplicity, we are using student_id as password
        query = """
        SELECT p.student_id, p.name, t.team_name
        FROM Player p
        JOIN Team t ON p.team_id = t.team_id
        WHERE p.student_id = %s AND p.role = '队长'
        """
        result = self.db_conn.execute_query(query, (student_id,))
        if result and password == student_id:  # Simple password check
            return result[0]
        return None

    def finalize_admin_login(self, username):
        QMessageBox.information(self, "Login Successful", f"Welcome back, Administrator!")
        self.on_admin_login()
        self.close()

    def finalize_captain_login(self, captain_info):
        QMessageBox.information(
            self,
            "Login Successful",
            f"Welcome, {captain_info['name']}!\n队长: {captain_info['team_name']}"
        )
        self.on_captain_login(captain_info['student_id'])
        self.close()

    def reset_login_button(self):
        self.is_loading = False
        self.login_btn.setText("Login")
        self.login_btn.setEnabled(True)