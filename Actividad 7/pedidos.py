from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt
from database import conectar

class VentanaPedidos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Pedidos")
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
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
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

        self.cliente = QLineEdit()
        self.importe = QLineEdit()
        self.estado = QLineEdit()
        self.descripcion = QLineEdit()

        left_layout.addWidget(QLabel("Cliente ID:"))
        left_layout.addWidget(self.cliente)
        left_layout.addWidget(QLabel("Importe:"))
        left_layout.addWidget(self.importe)
        left_layout.addWidget(QLabel("Estado:"))
        left_layout.addWidget(self.estado)
        left_layout.addWidget(QLabel("Descripción:"))
        left_layout.addWidget(self.descripcion)

        self.btn_guardar = QPushButton("Guardar Nuevo Pedido")
        self.btn_guardar.clicked.connect(self.guardar_o_actualizar)
        left_layout.addWidget(self.btn_guardar)

        btn_editar = QPushButton("Editar Seleccionado")
        btn_editar.clicked.connect(self.editar_seleccionado)
        left_layout.addWidget(btn_editar)

        form_layout.addLayout(left_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Cliente ID", "Fecha", "Importe", "Estado", "Descripción"])
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
        cursor.execute("SELECT id, cliente_id, fecha, importe, estado, descripcion FROM pedidos")
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
        self.cliente.setText(self.tabla.item(row, 1).text())
        self.importe.setText(self.tabla.item(row, 3).text())
        self.estado.setText(self.tabla.item(row, 4).text())
        self.descripcion.setText(self.tabla.item(row, 5).text())
        self.editando = True
        self.btn_guardar.setText("Actualizar Pedido")

    def guardar_o_actualizar(self):
        cliente = self.cliente.text()
        importe = self.importe.text()
        estado = self.estado.text()
        descripcion = self.descripcion.text()

        if not cliente.isdigit():
            QMessageBox.warning(self, "Error", "Cliente ID debe ser un número entero")
            return

        try:
            float(importe)
        except ValueError:
            QMessageBox.warning(self, "Error", "Importe debe ser un número")
            return

        conn = conectar()
        cursor = conn.cursor()
        try:
            if self.editando:
                cursor.execute("""
                UPDATE pedidos SET cliente_id=?, importe=?, estado=?, descripcion=?
                WHERE id=?
                """, (int(cliente), float(importe), estado, descripcion, self.id_editando))
            else:
                cursor.execute("""
                INSERT INTO pedidos(cliente_id, fecha, importe, estado, descripcion)
                VALUES (?, DATE('now'), ?, ?, ?)
                """, (int(cliente), float(importe), estado, descripcion))
            conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", str(e))
            conn.rollback()
        finally:
            conn.close()

        self.cliente.clear()
        self.importe.clear()
        self.estado.clear()
        self.descripcion.clear()
        self.editando = False
        self.id_editando = None
        self.btn_guardar.setText("Guardar Nuevo Pedido")
        self.cargar()

def ventana_pedidos():
    win = VentanaPedidos()
    win.show()
    return win