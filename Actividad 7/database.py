import sqlite3

DB_NAME = "empresa.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        telefono TEXT,
        email TEXT,
        empresa TEXT,
        fecha_alta TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        fecha TEXT,
        importe REAL,
        estado TEXT,
        descripcion TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )
    """)

    conn.commit()
    conn.close()

def crear_usuarios_prueba():
    conn = conectar()
    cursor = conn.cursor()

    usuarios = [
        ("admin","admin123","administrador"),
        ("ceo","ceo123","ceo")
    ]

    for u in usuarios:
        try:
            cursor.execute("INSERT INTO usuarios (username,password,rol) VALUES (?,?,?)", u)
        except:
            pass

    conn.commit()
    conn.close()