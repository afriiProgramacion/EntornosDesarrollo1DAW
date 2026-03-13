from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import conectar

class LoginWindow(QWidget):
    def __init__(self, open_panel_callback):
        super().__init__()
        self.open_panel_callback = open_panel_callback
        self.setWindowTitle("Login - Gestión Empresa")
        self.setGeometry(400, 300, 400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: Arial;
            }
            QLabel {
                font-size: 18px;
                color: #333;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 12px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("LOGIN")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        user_label = QLabel("Usuario:")
        layout.addWidget(user_label)
        self.user_entry = QLineEdit()
        layout.addWidget(self.user_entry)

        pass_label = QLabel("Contraseña:")
        layout.addWidget(pass_label)
        self.pass_entry = QLineEdit()
        self.pass_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_entry)

        login_btn = QPushButton("Entrar")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def login(self):
        username = self.user_entry.text()
        password = self.pass_entry.text()

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT rol FROM usuarios WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            rol = result[0]
            self.open_panel_callback(rol)
        else:
            QMessageBox.warning(self, "Error", "Login incorrecto")