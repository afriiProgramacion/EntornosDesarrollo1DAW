from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
from database import conectar
from validaciones import validar_email, validar_telefono
from datetime import date

class VentanaClientes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Clientes")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: Arial;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QTableWidget {
                gridline-color: #ddd;
            }
        """)

        layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        left_layout = QVBoxLayout()

        self.editando = False
        self.id_editando = None

        self.nombre = QLineEdit()
        self.telefono = QLineEdit()
        self.email = QLineEdit()
        self.empresa = QLineEdit()

        left_layout.addWidget(QLabel("Nombre:"))
        left_layout.addWidget(self.nombre)
        left_layout.addWidget(QLabel("Teléfono:"))
        left_layout.addWidget(self.telefono)
        left_layout.addWidget(QLabel("Email:"))
        left_layout.addWidget(self.email)
        left_layout.addWidget(QLabel("Empresa:"))
        left_layout.addWidget(self.empresa)

        self.btn_guardar = QPushButton("Guardar Nuevo Cliente")
        self.btn_guardar.clicked.connect(self.guardar_o_actualizar)
        left_layout.addWidget(self.btn_guardar)

        btn_editar = QPushButton("Editar Seleccionado")
        btn_editar.clicked.connect(self.editar_seleccionado)
        left_layout.addWidget(btn_editar)

        form_layout.addLayout(left_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Email", "Empresa"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        form_layout.addWidget(self.tabla)

        layout.addLayout(form_layout)

        self.setLayout(layout)
        self.cargar()

    def cargar(self):
        self.tabla.setRowCount(0)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, telefono, email, empresa FROM clientes")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            row_position = self.tabla.rowCount()
            self.tabla.insertRow(row_position)
            for col, data in enumerate(row):
                self.tabla.setItem(row_position, col, QTableWidgetItem(str(data)))

    def editar_seleccionado(self):
        selected_items = self.tabla.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        self.id_editando = int(self.tabla.item(row, 0).text())
        self.nombre.setText(self.tabla.item(row, 1).text())
        self.telefono.setText(self.tabla.item(row, 2).text())
        self.email.setText(self.tabla.item(row, 3).text())
        self.empresa.setText(self.tabla.item(row, 4).text())
        self.editando = True
        self.btn_guardar.setText("Actualizar Cliente")

    def guardar_o_actualizar(self):
        nombre = self.nombre.text()
        telefono = self.telefono.text()
        email = self.email.text()
        empresa = self.empresa.text()

        if not validar_email(email):
            QMessageBox.warning(self, "Error", "Email incorrecto")
            return

        if not validar_telefono(telefono):
            QMessageBox.warning(self, "Error", "Teléfono incorrecto")
            return

        conn = conectar()
        cursor = conn.cursor()
        if self.editando:
            cursor.execute("""
            UPDATE clientes SET nombre=?, telefono=?, email=?, empresa=?
            WHERE id=?
            """, (nombre, telefono, email, empresa, self.id_editando))
        else:
            cursor.execute("""
            INSERT INTO clientes(nombre, telefono, email, empresa, fecha_alta)
            VALUES (?, ?, ?, ?, ?)
            """, (nombre, telefono, email, empresa, str(date.today())))
        conn.commit()
        conn.close()

        self.nombre.clear()
        self.telefono.clear()
        self.email.clear()
        self.empresa.clear()
        self.editando = False
        self.id_editando = None
        self.btn_guardar.setText("Guardar Nuevo Cliente")
        self.cargar()

def ventana_clientes():
    win = VentanaClientes()
    win.show()
    return win