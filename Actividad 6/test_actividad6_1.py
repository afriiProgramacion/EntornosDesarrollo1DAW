"""Tests (pytest) para la Actividad 6_1.

Ejecutar desde la raíz del proyecto:
    pytest -q "Actividad 6/test_actividad6_1.py"
"""

from __future__ import annotations

import pytest

from calculadora_core import division, multiplicacion, resta, suma


def test_suma_2_3_es_5() -> None:
    assert suma(2, 3) == 5


def test_resta_5_2_es_3() -> None:
    assert resta(5, 2) == 3


def test_multiplicacion_3_4_es_12() -> None:
    assert multiplicacion(3, 4) == 12


def test_division_10_2_es_5() -> None:
    assert division(10, 2) == 5


def test_division_por_cero_controlada() -> None:
    with pytest.raises(ZeroDivisionError):
        division(10, 0)
