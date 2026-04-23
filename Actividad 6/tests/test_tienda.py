"""Actividad 6_2 — Pruebas unitarias con pytest para `tienda.py`.

Requisitos cubiertos:
- Tests para: obtener_producto, calcular_subtotal, aplicar_descuento,
  calcular_envio, calcular_total
- Casos normales, límite y erróneos
- Uso de fixtures
- Uso de parametrización
- Comprobación de excepciones con pytest.raises
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Asegura que el `tienda.py` de esta carpeta se pueda importar
# tanto al ejecutar `pytest` como al ejecutar este archivo directamente.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import tienda as tienda


# ------------------------
# Fixtures
# ------------------------


@pytest.fixture()
def lineas_validas() -> list[dict]:
    """Pedido válido con varias líneas (reutilizable)."""

    return [
        {"producto": "teclado", "cantidad": 2},
        {"producto": "raton", "cantidad": 1},
    ]


@pytest.fixture()
def pedido_valido(lineas_validas: list[dict]) -> dict:
    """Pedido completo válido."""

    return {
        "lineas": lineas_validas,
        "provincia": "Sevilla",
        "es_vip": False,
        "cupon": None,
        "urgente": False,
    }


# ------------------------
# obtener_producto
# ------------------------


def test_obtener_producto_devuelve_dict_con_precio_y_stock() -> None:
    p = tienda.obtener_producto("teclado")
    assert isinstance(p, dict)
    assert "precio" in p and "stock" in p
    assert p["precio"] > 0


def test_obtener_producto_inexistente_lanza_keyerror() -> None:
    with pytest.raises(KeyError, match=r"Producto no encontrado"):
        tienda.obtener_producto("inexistente")


# ------------------------
# calcular_subtotal
# ------------------------


@pytest.mark.parametrize(
    "lineas, esperado",
    [
        ([{"producto": "usb", "cantidad": 1}], 8.00),
        ([{"producto": "usb", "cantidad": 3}], 24.00),
        (
            [
                {"producto": "teclado", "cantidad": 2},
                {"producto": "raton", "cantidad": 1},
            ],
            65.00,
        ),
    ],
)
def test_calcular_subtotal_casos_normales(lineas: list[dict], esperado: float) -> None:
    assert tienda.calcular_subtotal(lineas) == pytest.approx(esperado)


def test_calcular_subtotal_pedido_vacio_lanza_error() -> None:
    with pytest.raises(tienda.PedidoInvalidoError, match=r"vac[ií]o"):
        tienda.calcular_subtotal([])


@pytest.mark.parametrize("cantidad", [0, -1, -10])
def test_calcular_subtotal_cantidad_no_valida_lanza_error(cantidad: int) -> None:
    lineas = [{"producto": "usb", "cantidad": cantidad}]
    with pytest.raises(tienda.PedidoInvalidoError, match=r"mayor que cero"):
        tienda.calcular_subtotal(lineas)


def test_calcular_subtotal_stock_insuficiente_lanza_error() -> None:
    # monitor tiene stock 5
    lineas = [{"producto": "monitor", "cantidad": 6}]
    with pytest.raises(tienda.ProductoNoDisponibleError, match=r"Stock insuficiente"):
        tienda.calcular_subtotal(lineas)


def test_calcular_subtotal_producto_inexistente_lanza_keyerror() -> None:
    lineas = [{"producto": "no_existe", "cantidad": 1}]
    with pytest.raises(KeyError, match=r"Producto no encontrado"):
        tienda.calcular_subtotal(lineas)


# ------------------------
# aplicar_descuento
# ------------------------


@pytest.mark.parametrize(
    "subtotal, es_vip, cupon, esperado",
    [
        (100.0, False, None, 100.0),
        (100.0, True, None, 90.0),
        (100.0, False, "PROMO5", 95.0),
        (100.0, False, "PROMO10", 90.0),
        (100.0, True, "PROMO5", 85.0),
        (100.0, True, "PROMO10", 80.0),
        (99.99, True, "PROMO10", 79.99),  # redondeo
        (50.0, False, "CUPON_INVENTADO", 50.0),
    ],
)
def test_aplicar_descuento_parametrizado(
    subtotal: float, es_vip: bool, cupon: str | None, esperado: float
) -> None:
    assert tienda.aplicar_descuento(subtotal, es_vip=es_vip, cupon=cupon) == pytest.approx(esperado)


# ------------------------
# calcular_envio
# ------------------------


@pytest.mark.parametrize(
    "subtotal, provincia, urgente, esperado",
    [
        (100.0, "sevilla", False, 0.0),
        (99.99, "sevilla", False, 6.5),
        (50.0, "Baleares", False, 14.5),
        (50.0, "canarias", True, 19.5),  # 6.5 + 8 + 5
        (150.0, "canarias", True, 13.0),  # 0 + 8 + 5
    ],
)
def test_calcular_envio_parametrizado(
    subtotal: float, provincia: str, urgente: bool, esperado: float
) -> None:
    assert tienda.calcular_envio(subtotal, provincia, urgente=urgente) == pytest.approx(esperado)


# ------------------------
# calcular_total
# ------------------------


def test_calcular_total_caso_normal(lineas_validas: list[dict]) -> None:
    # subtotal: 2*25 + 1*15 = 65
    # sin descuento
    # envio: 6.5
    assert tienda.calcular_total(lineas_validas, "Sevilla") == pytest.approx(71.5)


def test_calcular_total_usa_subtotal_con_descuento_para_envio(lineas_validas: list[dict]) -> None:
    # subtotal = 65
    # VIP 10% -> 58.50
    # envio se calcula con subtotal_desc (58.50 < 100 => 6.5)
    total = tienda.calcular_total(lineas_validas, "Sevilla", es_vip=True)
    assert total == pytest.approx(65.0)


def test_calcular_total_con_envio_gratis_por_superar_100_sin_descuento() -> None:
    # monitor 120, cantidad 1 => subtotal 120, envío 0
    lineas = [{"producto": "monitor", "cantidad": 1}]
    assert tienda.calcular_total(lineas, "Sevilla") == pytest.approx(120.0)


def test_calcular_total_propagacion_error_pedido_vacio() -> None:
    with pytest.raises(tienda.PedidoInvalidoError):
        tienda.calcular_total([], "Sevilla")


# ------------------------
# (Extra útil) API externa simulada + persistencia
# No lo exige el enunciado, pero ayuda a validar comportamiento.
# ------------------------


@pytest.mark.parametrize(
    "codigo, esperado",
    [
        ("OK123", {"estado": "en reparto", "incidencia": False}),
        ("ERR999", {"estado": "desconocido", "incidencia": True}),
    ],
)
def test_consultar_estado_envio_casos_normales(codigo: str, esperado: dict) -> None:
    assert tienda.consultar_estado_envio(codigo) == esperado


def test_consultar_estado_envio_error_conexion() -> None:
    with pytest.raises(ConnectionError):
        tienda.consultar_estado_envio("XYZ")


def test_guardar_y_cargar_pedido(tmp_path, pedido_valido: dict) -> None:
    # tmp_path es un fixture built-in; aquí se usa para no escribir en carpetas reales.
    ruta = tmp_path / "pedido.json"
    assert tienda.guardar_pedido(ruta, pedido_valido) is True
    loaded = tienda.cargar_pedido(ruta)
    assert loaded == pedido_valido


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
