"""Lógica de la calculadora (Actividad 6_1).

Este módulo contiene únicamente funciones puras para poder reutilizarlas:
- desde la interfaz (Tkinter)
- desde las pruebas unitarias (pytest)
"""

from __future__ import annotations


def suma(a: float, b: float) -> float:
    """Suma dos números."""

    return a + b


def resta(a: float, b: float) -> float:
    """Resta dos números."""

    return a - b


def multiplicacion(a: float, b: float) -> float:
    """Multiplica dos números."""

    return a * b


def division(a: float, b: float) -> float:
    """Divide dos números.

    Lanza
    -----
    ZeroDivisionError
        Si b es 0.
    """

    if b == 0:
        raise ZeroDivisionError("división por cero")
    return a / b
