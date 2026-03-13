import matplotlib.pyplot as plt
from database import conectar

def pedidos_por_estado():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT estado, COUNT(*) FROM pedidos
    GROUP BY estado
    """)

    datos = cursor.fetchall()

    estados = [d[0] for d in datos]
    cantidades = [d[1] for d in datos]

    plt.bar(estados,cantidades)

    plt.title("Pedidos por estado")

    plt.show()

    conn.close()