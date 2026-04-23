"""Actividad 6_1 — Calculadora Tkinter con pruebas unitarias integradas.

Requisitos del ejercicio:
- Calculadora básica con interfaz gráfica (Tkinter)
- Funciones independientes: suma, resta, multiplicacion, division
- Botón "Pruebas" que ejecuta pruebas unitarias y muestra resultados
- Pruebas implementadas con pytest (ver test_actividad6_1.py)
- Sin librerías externas adicionales (solo pytest para testing)

Ejecutar:
    python "Actividad 6/actividad6.1.py"

Nota:
- Si no tienes pytest instalado, el botón "Pruebas" avisará.
"""

from __future__ import annotations

import importlib
import math
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from tkinter import scrolledtext

from calculadora_core import division, multiplicacion, resta, suma
@dataclass
class TestResult:
    """Resultado simple de un test para mostrarlo en pantalla."""

    name: str
    passed: bool
    details: str = ""


class PytestCapturePlugin:
    """Plugin minimalista para capturar resultados de pytest."""

    def __init__(self) -> None:
        self.results: list[TestResult] = []

    def pytest_runtest_logreport(self, report):  # noqa: ANN001
        # report.when: setup/call/teardown
        if report.when != "call":
            return

        if report.passed:
            self.results.append(TestResult(name=report.nodeid, passed=True))
        elif report.failed:
            # report.longrepr puede ser enorme, pero para clase vale un resumen.
            summary = str(report.longrepr)
            self.results.append(TestResult(name=report.nodeid, passed=False, details=summary))


class CalculatorApp(tk.Tk):
    """Ventana principal de la calculadora con botón de pruebas."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Actividad 6_1 — Calculadora")
        self.geometry("760x560")
        self.minsize(740, 520)

        self._op: str | None = None

        # Tema oscuro suave ("negro muy clarito" = gris muy oscuro)
        bg = "#202020"
        fg = "#f2f2f2"
        panel = "#2a2a2a"
        input_bg = "#2d2d2d"

        self.configure(bg=bg)

        style = ttk.Style(self)
        # Usamos un tema que permita recolorear correctamente en ttk.
        try:
            style.theme_use("clam")
        except Exception:  # noqa: BLE001
            pass

        style.configure("App.TFrame", background=bg)
        style.configure(
            "App.TLabelframe",
            background=bg,
            foreground=fg,
            bordercolor=panel,
        )
        style.configure("App.TLabelframe.Label", background=bg, foreground=fg)
        style.configure("App.TLabel", background=bg, foreground=fg)

        style.configure(
            "App.TEntry",
            fieldbackground=input_bg,
            background=input_bg,
            foreground=fg,
            insertcolor=fg,
        )
        style.map(
            "App.TEntry",
            fieldbackground=[("readonly", input_bg)],
            foreground=[("readonly", fg)],
        )

        style.configure(
            "Calc.TButton",
            padding=(12, 10),
            background=panel,
            foreground=fg,
        )
        style.configure(
            "Op.TButton",
            padding=(12, 10),
            background=panel,
            foreground=fg,
        )

        outer = ttk.Frame(self, padding=12, style="App.TFrame")
        outer.pack(fill=tk.BOTH, expand=True)

        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)

        # Display tipo calculadora (resultado / estado)
        self.display_var = tk.StringVar(value="0")
        self.display = ttk.Entry(
            outer,
            textvariable=self.display_var,
            justify="right",
            font=("Segoe UI", 18, "bold"),
            style="App.TEntry",
        )
        self.display.state(["readonly"])
        self.display.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Entradas numéricas
        frm_top = ttk.LabelFrame(outer, text="Entradas", padding=10, style="App.TLabelframe")
        frm_top.grid(row=1, column=0, sticky="ew")
        frm_top.columnconfigure(1, weight=1)
        frm_top.columnconfigure(3, weight=1)

        ttk.Label(frm_top, text="Número 1:", style="App.TLabel").grid(row=0, column=0, sticky="w")
        self.entry_a = ttk.Entry(frm_top, style="App.TEntry")
        self.entry_a.grid(row=0, column=1, sticky="ew", padx=(6, 14))

        ttk.Label(frm_top, text="Número 2:", style="App.TLabel").grid(row=0, column=2, sticky="w")
        self.entry_b = ttk.Entry(frm_top, style="App.TEntry")
        self.entry_b.grid(row=0, column=3, sticky="ew", padx=(6, 0))

        # Botones estilo calculadora
        frm_calc = ttk.Frame(outer, style="App.TFrame")
        frm_calc.grid(row=2, column=0, sticky="ew", pady=(10, 8))
        frm_calc.columnconfigure(0, weight=1)
        frm_calc.columnconfigure(1, weight=1)
        frm_calc.columnconfigure(2, weight=1)
        frm_calc.columnconfigure(3, weight=1)
        frm_calc.columnconfigure(4, weight=1)
        frm_calc.columnconfigure(5, weight=1)

        self.lbl_selected = ttk.Label(frm_calc, text="Operación: (elige una)", style="App.TLabel")
        self.lbl_selected.grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 6))

        ttk.Button(frm_calc, text="+", style="Op.TButton", command=lambda: self._select_op("+"))\
            .grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        ttk.Button(frm_calc, text="-", style="Op.TButton", command=lambda: self._select_op("-"))\
            .grid(row=1, column=1, sticky="ew", padx=4, pady=4)
        ttk.Button(frm_calc, text="×", style="Op.TButton", command=lambda: self._select_op("*"))\
            .grid(row=1, column=2, sticky="ew", padx=4, pady=4)
        ttk.Button(frm_calc, text="÷", style="Op.TButton", command=lambda: self._select_op("/"))\
            .grid(row=1, column=3, sticky="ew", padx=4, pady=4)

        ttk.Button(frm_calc, text="=", style="Calc.TButton", command=self._calculate)\
            .grid(row=1, column=4, sticky="ew", padx=(14, 4), pady=4)
        ttk.Button(frm_calc, text="Pruebas", style="Calc.TButton", command=self._run_tests)\
            .grid(row=1, column=5, sticky="ew", padx=4, pady=4)

        # Salida / pruebas
        frm_out = ttk.LabelFrame(outer, text="Salida / pruebas", padding=10, style="App.TLabelframe")
        frm_out.grid(row=3, column=0, sticky="nsew")
        frm_out.rowconfigure(0, weight=1)
        frm_out.columnconfigure(0, weight=1)

        self.txt_out = scrolledtext.ScrolledText(frm_out, height=18, wrap=tk.WORD)
        self.txt_out.grid(row=0, column=0, sticky="nsew")

        # Colores del Text (tk) para que encaje con el tema oscuro
        self.txt_out.configure(bg=input_bg, fg=fg, insertbackground=fg)

        # Tags de color (ampliación opcional)
        self.txt_out.tag_configure("ok", foreground="#7ee787")
        self.txt_out.tag_configure("fail", foreground="#ff7b72")
        self.txt_out.tag_configure("info", foreground="#c9d1d9")

        self._set_output(
            "Calculadora lista.\n"
            "- Introduce los dos números.\n"
            "- Elige operación (+, -, ×, ÷).\n"
            "- Pulsa '=' para calcular.\n"
            "- Pulsa 'Pruebas' para ejecutar pytest.\n"
        )

        self.entry_a.focus_set()

    def _select_op(self, op: str) -> None:
        """Selecciona la operación para el botón '='."""

        self._op = op
        symbol = {"*": "×", "/": "÷"}.get(op, op)
        self.lbl_selected.configure(text=f"Operación: {symbol}")

    def _parse_float(self, text: str) -> float:
        """Convierte la entrada del usuario a float (acepta coma)."""

        cleaned = text.strip().replace(",", ".")
        if cleaned == "":
            raise ValueError("entrada vacía")
        value = float(cleaned)
        if not math.isfinite(value):
            raise ValueError("número no válido")
        return value

    def _calculate(self) -> None:
        """Calcula el resultado con la operación seleccionada."""

        self._clear_output()

        if self._op is None:
            self._append_output("❌ Elige una operación primero.\n", tag="fail")
            return

        try:
            a = self._parse_float(self.entry_a.get())
            b = self._parse_float(self.entry_b.get())

            if self._op == "+":
                res = suma(a, b)
            elif self._op == "-":
                res = resta(a, b)
            elif self._op == "*":
                res = multiplicacion(a, b)
            elif self._op == "/":
                res = division(a, b)
            else:
                raise ValueError("operación desconocida")

            self._set_display(str(res))
            self._append_output(f"✔ Resultado calculado: {res}\n", tag="ok")
        except ZeroDivisionError:
            self._set_display("Error")
            self._append_output("❌ Error: división por cero\n", tag="fail")
        except Exception as exc:  # noqa: BLE001
            self._set_display("Error")
            self._append_output(f"❌ Error: {exc}\n", tag="fail")

    def _run_tests(self) -> None:
        """Ejecuta pytest y muestra los resultados en la pantalla."""

        self._clear_output()

        try:
            pytest = importlib.import_module("pytest")
        except Exception:  # noqa: BLE001
            self._append_output("❌ No se pudo importar pytest.\n", tag="fail")
            self._append_output("Instala pytest con: pip install pytest\n", tag="info")
            return

        plugin = PytestCapturePlugin()

        # Ejecuta SOLO los tests de esta actividad (sin recorrer toda la carpeta).
        # Ruta relativa desde el directorio donde se ejecuta el script.
        test_path = "Actividad 6/test_actividad6_1.py"

        # -q: salida corta, --disable-warnings: para no ensuciar
        exit_code = pytest.main(["-q", "--disable-warnings", test_path], plugins=[plugin])

        ok = 0
        total = 0
        for r in plugin.results:
            total += 1
            name_short = r.name.split("::")[-1]
            if r.passed:
                ok += 1
                self._append_output(f"✔ {name_short} correcta\n", tag="ok")
            else:
                self._append_output(f"❌ {name_short} fallida\n", tag="fail")

        # Si por alguna razón no se ha recogido nada (p.ej. ruta mal), avisamos.
        if total == 0:
            self._append_output("❌ No se han encontrado/ejecutado tests.\n", tag="fail")
            self._append_output(f"Código salida pytest: {exit_code}\n", tag="info")
            self._set_display("Pruebas fallidas")
            return

        if ok == total and exit_code == 0:
            self._set_display("Pruebas correctas")
        else:
            self._set_display("Pruebas fallidas")

        self._append_output(f"Resultado: {ok}/{total} pruebas correctas\n", tag="info")

    def _set_display(self, text: str) -> None:
        self.display.state(["!readonly"])
        self.display_var.set(text)
        self.display.state(["readonly"])

    def _clear_output(self) -> None:
        self.txt_out.configure(state="normal")
        self.txt_out.delete("1.0", tk.END)
        self.txt_out.configure(state="disabled")

    def _set_output(self, text: str) -> None:
        self.txt_out.configure(state="normal")
        self.txt_out.delete("1.0", tk.END)
        self.txt_out.insert(tk.END, text)
        self.txt_out.configure(state="disabled")

    def _append_output(self, text: str, tag: str | None = None) -> None:
        self.txt_out.configure(state="normal")
        if tag:
            self.txt_out.insert(tk.END, text, tag)
        else:
            self.txt_out.insert(tk.END, text)
        self.txt_out.configure(state="disabled")


def main() -> int:
    """Punto de entrada."""

    app = CalculatorApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
