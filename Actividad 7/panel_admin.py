from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from clientes import ventana_clientes
from pedidos import ventana_pedidos
from exportacion import exportar_clientes

class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panel Administrador - Gestión Empresa")
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
                background-color: #28a745;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                border-radius: 8px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("PANEL ADMINISTRADOR")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        btn_clientes = QPushButton("Gestionar Clientes")
        btn_clientes.clicked.connect(self.abrir_clientes)
        layout.addWidget(btn_clientes)

        btn_pedidos = QPushButton("Gestionar Pedidos")
        btn_pedidos.clicked.connect(self.abrir_pedidos)
        layout.addWidget(btn_pedidos)

        btn_exportar = QPushButton("Exportar Clientes a CSV")
        btn_exportar.clicked.connect(exportar_clientes)
        layout.addWidget(btn_exportar)

        self.setLayout(layout)
        self.ventanas_abiertas = []

    def abrir_clientes(self):
        from clientes import ventana_clientes
        win = ventana_clientes()
        self.ventanas_abiertas.append(win)

    def abrir_pedidos(self):
        from pedidos import ventana_pedidos
        win = ventana_pedidos()
        self.ventanas_abiertas.append(win)