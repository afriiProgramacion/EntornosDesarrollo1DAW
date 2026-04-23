"""Actividad 5_2

Una empresa de transporte debe repartir abono en las marismas de Trebujena.
Se generan 100.000 fincas con necesidades de abono entre 50 y 500 kg.
Se calcula el total con un incremento del 10% (pérdidas en el camino)
y se compara el tiempo usando:
1) Listas tradicionales
2) Listas con comprensión
3) Generadores
"""

from __future__ import annotations

import random
import time

N_FINCA = 100_000
MIN_KG = 50
MAX_KG = 500
INCREMENTO = 0.10
SEED = 20260406


def total_con_incremento(total_base: int | float) -> float:
    return total_base * (1.0 + INCREMENTO)


def lista_tradicional(n: int, seed: int) -> float:
    rng = random.Random(seed)
    cantidades: list[int] = []
    for _ in range(n):
        cantidades.append(rng.randint(MIN_KG, MAX_KG))
    return total_con_incremento(sum(cantidades))


def list_comprehension(n: int, seed: int) -> float:
    rng = random.Random(seed)
    cantidades = [rng.randint(MIN_KG, MAX_KG) for _ in range(n)]
    return total_con_incremento(sum(cantidades))


def generador(n: int, seed: int) -> float:
    rng = random.Random(seed)
    cantidades = (rng.randint(MIN_KG, MAX_KG) for _ in range(n))
    return total_con_incremento(sum(cantidades))


def medir(fn, n: int, seed: int) -> tuple[float, float]:
    inicio = time.perf_counter()
    total = fn(n, seed)
    fin = time.perf_counter()
    return total, fin - inicio


def main() -> None:
    total1, t1 = medir(lista_tradicional, N_FINCA, SEED)
    print("=== LISTA TRADICIONAL ===")
    print(f"Total: {total1:.2f}")
    print(f"Tiempo: {t1:.6f}")

    total2, t2 = medir(list_comprehension, N_FINCA, SEED)
    print("=== LIST COMPREHENSION ===")
    print(f"Total: {total2:.2f}")
    print(f"Tiempo: {t2:.6f}")

    total3, t3 = medir(generador, N_FINCA, SEED)
    print("=== GENERADOR ===")
    print(f"Total: {total3:.2f}")
    print(f"Tiempo: {t3:.6f}")


if __name__ == "__main__":
    main()
