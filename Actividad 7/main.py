import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from database import crear_tablas, crear_usuarios_prueba
from login import LoginWindow
from panel_admin import AdminPanel
from panel_ceo import CEOPanel

crear_tablas()
crear_usuarios_prueba()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión Empresa - Profesional")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QLabel {
                font-size: 16px;
                color: #333;
            }
        """)
        self.login_window = LoginWindow(self.open_panel)
        self.login_window.show()

    def open_panel(self, rol):
        self.login_window.close()
        if rol == "administrador":
            self.admin_panel = AdminPanel()
            self.admin_panel.show()
        elif rol == "ceo":
            self.ceo_panel = CEOPanel()
            self.ceo_panel.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())