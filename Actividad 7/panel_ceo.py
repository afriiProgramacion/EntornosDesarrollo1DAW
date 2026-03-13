from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from graficas import pedidos_por_estado

class CEOPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panel CEO - Gestión Empresa")
        self.setGeometry(200, 200, 600, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: Arial;
            }
            QLabel {
                font-size: 24px;
                color: #495057;
                font-weight: bold;
            }
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                border-radius: 8px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("PANEL CEO")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        btn_graficas = QPushButton("Ver Gráficas de Pedidos")
        btn_graficas.clicked.connect(pedidos_por_estado)
        layout.addWidget(btn_graficas)

        self.setLayout(layout)