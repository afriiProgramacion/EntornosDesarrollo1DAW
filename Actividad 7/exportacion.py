import csv
from database import conectar

def exportar_clientes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes")
    datos = cursor.fetchall()

    with open("clientes.csv","w",newline="",encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
        "id","nombre","telefono","email","empresa","fecha"
        ])

        writer.writerows(datos)

    conn.close()