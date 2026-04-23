"""Actividad 5_3 — Comparación de optimización y documentación en Python.

Objetivo
Crear una aplicación con interfaz gráfica (Tkinter) que compare en tiempo real:
- una versión NO optimizada
- una versión optimizada

La aplicación obtiene datos de una API relacionada con el espacio (posición de la ISS)
y actualiza la información cada pocos segundos. En cada panel se muestran:
- datos obtenidos
- tiempo de ejecución (procesado)
- hora de actualización
- indicador visual de estado
- resumen de cProfile (funciones más lentas)

Además, cada panel incluye un botón Help que abre una ventana con la documentación
(docstrings) de las funciones relevantes.

API usada
- https://api.wheretheiss.at/v1/satellites/25544

Ejecutar
- python "Actividad 5/actividad5.3.py"
"""

from __future__ import annotations

import cProfile
import datetime as _dt
import inspect
import io
import json
import math
import pstats
import sys
import time
import tkinter as tk
from collections import deque
from dataclasses import dataclass
from tkinter import scrolledtext
from urllib.error import URLError
from urllib.request import Request, urlopen

ISS_API_URL = "https://api.wheretheiss.at/v1/satellites/25544"
ISS_FALLBACK_URL = "http://api.open-notify.org/iss-now.json"
UPDATE_MS = 3000
HISTORY_SIZE = 120


class DemoIssSimulator:
    """Simulador simple para cuando no hay conexión.

    Genera una trayectoria "creíble" (random-walk suave) para que la app
    pueda demostrar:
    - actualización periódica
    - comparación de paneles
    - tiempos y profiling
    incluso si la red del centro bloquea las APIs.
    """

    def __init__(self) -> None:
        self._lat = 0.0
        self._lon = 0.0
        self._vel = 27600.0  # km/h aprox. órbita baja
        self._alt = 420.0
        self._step = 0

    def next_payload(self) -> dict:
        """Devuelve un payload con el mismo formato que la API principal."""

        self._step += 1

        # Movimiento suave determinista (sin random para que sea repetible)
        self._lat = 20.0 * math.sin(self._step / 15.0)
        self._lon = (self._lon + 3.5) % 360.0
        if self._lon > 180:
            self._lon -= 360

        self._vel = 27600.0 + 120.0 * math.sin(self._step / 10.0)
        self._alt = 420.0 + 5.0 * math.sin(self._step / 8.0)

        return {
            "timestamp": int(time.time()),
            "latitude": float(self._lat),
            "longitude": float(self._lon),
            "velocity": float(self._vel),
            "altitude": float(self._alt),
            "source": "DEMO (sin Internet)",
        }


@dataclass(frozen=True)
class IssSample:
    """Muestra simplificada de datos de la ISS.

    Parameters
    ----------
    timestamp:
        Tiempo UNIX (segundos).
    latitude:
        Latitud en grados.
    longitude:
        Longitud en grados.
    velocity:
        Velocidad (km/h) según la API.
    altitude:
        Altitud (km) según la API.

    Returns
    -------
    IssSample
        Objeto inmutable con datos numéricos básicos.
    """

    timestamp: int
    latitude: float
    longitude: float
    velocity: float
    altitude: float


def _fetch_json(url: str, timeout_s: float) -> dict:
    """Descarga un JSON desde `url` usando librería estándar."""

    req = Request(url, headers={"User-Agent": "Actividad5_3/1.0"})
    with urlopen(req, timeout=timeout_s) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def fetch_iss_payload(timeout_s: float = 5.0) -> dict:
    """Descarga el JSON de una API de la ISS (con fallback).

    Intenta primero la API principal (wheretheiss). Si falla por red, usa
    una API alternativa (open-notify). El resultado se normaliza a un dict con:
    - timestamp, latitude, longitude, velocity, altitude
    - source (para mostrar de qué API viene)

    Parameters
    ----------
    timeout_s:
        Timeout de red en segundos.

    Returns
    -------
    dict
        Diccionario normalizado.

    Raises
    ------
    URLError
        Si fallan ambas APIs por red.
    ValueError
        Si el JSON no se puede decodificar.
    """

    try:
        payload = _fetch_json(ISS_API_URL, timeout_s)
        payload["source"] = "wheretheiss.at"
        return payload
    except URLError:
        # Fallback: open-notify (no trae velocidad/altitud)
        payload2 = _fetch_json(ISS_FALLBACK_URL, timeout_s)
        iss_pos = payload2.get("iss_position", {}) if isinstance(payload2, dict) else {}
        normalized = {
            "timestamp": int(payload2.get("timestamp", 0)),
            "latitude": float(iss_pos.get("latitude", 0.0)),
            "longitude": float(iss_pos.get("longitude", 0.0)),
            "velocity": 0.0,
            "altitude": 0.0,
            "source": "open-notify.org (sin vel/alt)",
        }
        return normalized


def payload_to_sample(payload: dict) -> IssSample:
    """Convierte el payload de la API a un IssSample.

    Parameters
    ----------
    payload:
        Diccionario JSON devuelto por la API.

    Returns
    -------
    IssSample
        Muestra con tipos numéricos.
    """

    return IssSample(
        timestamp=int(payload.get("timestamp", 0)),
        latitude=float(payload.get("latitude", 0.0)),
        longitude=float(payload.get("longitude", 0.0)),
        velocity=float(payload.get("velocity", 0.0)),
        altitude=float(payload.get("altitude", 0.0)),
    )


def unix_to_local_time_str(ts: int) -> str:
    """Convierte un timestamp UNIX a una hora local legible."""

    if ts <= 0:
        return "(sin hora)"
    dt = _dt.datetime.fromtimestamp(ts)
    return dt.strftime("%H:%M:%S")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia aproximada entre dos puntos usando Haversine.

    Parameters
    ----------
    lat1, lon1, lat2, lon2:
        Coordenadas en grados.

    Returns
    -------
    float
        Distancia en kilómetros.
    """

    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def profile_to_text(prof: cProfile.Profile, top_n: int = 10) -> str:
    """Convierte un objeto Profile en texto legible (top N por cumtime)."""

    s = io.StringIO()
    stats = pstats.Stats(prof, stream=s)
    stats.sort_stats("cumtime")
    stats.print_stats(top_n)
    return s.getvalue()


def show_help_dialog(parent: tk.Tk | tk.Toplevel, title: str, functions: list[object]) -> None:
    """Abre una ventana emergente con docstrings de las funciones dadas."""

    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry("780x520")

    txt = scrolledtext.ScrolledText(win, wrap=tk.WORD)
    txt.pack(fill=tk.BOTH, expand=True)

    for obj in functions:
        name = getattr(obj, "__name__", obj.__class__.__name__)
        doc = inspect.getdoc(obj) or "(Sin docstring)"
        txt.insert(tk.END, f"### {name}\n\n{doc}\n\n")

    txt.configure(state="disabled")


class PanelBase(tk.Frame):
    """Panel base con UI común para las dos versiones."""

    def __init__(self, master: tk.Misc, title: str, plot_color: str) -> None:
        super().__init__(master, bd=2, relief=tk.GROOVE, padx=8, pady=8)
        self.title = title
        self._plot_color = plot_color
        self._exec_history_s: deque[float] = deque(maxlen=60)

        self.lbl_title = tk.Label(self, text=title, font=("Segoe UI", 12, "bold"))
        self.lbl_title.pack(anchor="w")

        self.lbl_status = tk.Label(self, text="Estado: esperando...", bg="#dddddd", anchor="w")
        self.lbl_status.pack(fill=tk.X, pady=(6, 0))

        self.lbl_data = tk.Label(self, text="Datos: -", justify=tk.LEFT, anchor="w")
        self.lbl_data.pack(fill=tk.X, pady=(6, 0))

        self.lbl_time = tk.Label(self, text="Tiempo de ejecución: -", anchor="w")
        self.lbl_time.pack(fill=tk.X)

        tk.Label(self, text="Gráfico tiempo (ms):", anchor="w").pack(fill=tk.X, pady=(6, 0))
        self.canvas = tk.Canvas(self, height=90, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill=tk.X)

        self.lbl_exec_stats = tk.Label(self, text="Media/Min/Max: -", anchor="w")
        self.lbl_exec_stats.pack(fill=tk.X, pady=(2, 0))

        self.lbl_updated = tk.Label(self, text="Hora de actualización: -", anchor="w")
        self.lbl_updated.pack(fill=tk.X)

        self.btn_help = tk.Button(self, text="Help", command=self._on_help)
        self.btn_help.pack(anchor="e", pady=(6, 6))

        tk.Label(self, text="cProfile (top funciones):", anchor="w").pack(fill=tk.X)
        self.txt_profile = scrolledtext.ScrolledText(self, height=10, wrap=tk.NONE)
        self.txt_profile.pack(fill=tk.BOTH, expand=True)

    def _set_ok(self, msg: str) -> None:
        self.lbl_status.configure(text=f"Estado: {msg}", bg="#b7f0b1")

    def _set_warn(self, msg: str) -> None:
        self.lbl_status.configure(text=f"Estado: {msg}", bg="#f7e7a5")

    def _set_error(self, msg: str) -> None:
        self.lbl_status.configure(text=f"Estado: {msg}", bg="#f2b3b3")

    def _set_profile_text(self, text: str) -> None:
        self.txt_profile.configure(state="normal")
        self.txt_profile.delete("1.0", tk.END)
        self.txt_profile.insert(tk.END, text)
        self.txt_profile.configure(state="disabled")

    def _draw_exec_plot(self) -> None:
        """Dibuja un mini-gráfico del tiempo de ejecución (ms) usando Canvas."""
        self.canvas.update_idletasks()
        w = max(1, int(self.canvas.winfo_width()))
        h = max(1, int(self.canvas.winfo_height()))
        self.canvas.delete("all")

        if len(self._exec_history_s) < 2:
            self.canvas.create_text(6, h // 2, text="(esperando datos...)", anchor="w", fill="#666666")
            return

        values_ms = [v * 1000.0 for v in self._exec_history_s]
        vmin = min(values_ms)
        vmax = max(values_ms)
        if abs(vmax - vmin) < 1e-9:
            vmax = vmin + 1.0

        avg = sum(values_ms) / len(values_ms)
        self.lbl_exec_stats.configure(text=f"Media/Min/Max: {avg:.2f} / {vmin:.2f} / {vmax:.2f} ms")

        pad_x = 8
        pad_y = 10
        n = len(values_ms)
        dx = (w - 2 * pad_x) / (n - 1)

        # Línea base y etiquetas simples
        self.canvas.create_line(pad_x, h - pad_y, w - pad_x, h - pad_y, fill="#dddddd")
        self.canvas.create_text(w - pad_x, pad_y, text=f"max {vmax:.2f}", anchor="ne", fill="#666666")
        self.canvas.create_text(w - pad_x, h - pad_y, text=f"min {vmin:.2f}", anchor="se", fill="#666666")

        points: list[float] = []
        for i, v in enumerate(values_ms):
            x = pad_x + i * dx
            y = pad_y + (h - 2 * pad_y) * (1.0 - (v - vmin) / (vmax - vmin))
            points.extend([x, y])

        self.canvas.create_line(*points, fill=self._plot_color, width=2)

    def update_from_payload(self, payload: dict) -> None:
        """Actualiza el panel a partir de un payload JSON (medición + profiling)."""

        prof = cProfile.Profile()
        start = time.perf_counter()
        try:
            prof.enable()
            data_lines = self.process_payload(payload)
            prof.disable()
            elapsed = time.perf_counter() - start

            self._exec_history_s.append(elapsed)

            self.lbl_data.configure(text="Datos:\n" + "\n".join(data_lines))
            self.lbl_time.configure(text=f"Tiempo de ejecución: {elapsed:.6f} s")
            ts = int(payload.get("timestamp", 0))
            source = payload.get("source", "API")
            self.lbl_updated.configure(
                text=f"Hora de actualización: {unix_to_local_time_str(ts)}  |  Fuente: {source}"
            )
            self._set_ok("ok")
            self._draw_exec_plot()
            self._set_profile_text(profile_to_text(prof, top_n=12))
        except Exception as exc:  # noqa: BLE001 (se muestra al alumno)
            prof.disable()
            self._set_error(str(exc))
            self._draw_exec_plot()
            self._set_profile_text(profile_to_text(prof, top_n=12))

    def process_payload(self, payload: dict) -> list[str]:
        """Procesa el payload y devuelve líneas de texto para mostrar.

        Debe ser implementado por cada versión.
        """

        raise NotImplementedError

    def _on_help(self) -> None:
        raise NotImplementedError


class SlowPanel(PanelBase):
    """Versión NO optimizada (intencionadamente ineficiente)."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, title="Versión NO optimizada", plot_color="#d9534f")
        self.history: list[dict] = []

    def process_payload(self, payload: dict) -> list[str]:
        """Procesa datos usando listas y cálculos repetidos.

        Ejemplos de ineficiencia intencionada:
        - Copias completas de listas
        - Conversiones repetidas
        - Múltiples bucles para min/max/media
        - Recalcular distancias desde cero en cada actualización
        """

        self.history.append(payload)
        if len(self.history) > HISTORY_SIZE:
            self.history = self.history[-HISTORY_SIZE:]

        # Extraer listas (repetición + copias)
        lats = []
        lons = []
        vels = []
        alts = []
        for item in list(self.history):
            lats.append(float(item.get("latitude", 0.0)))
            lons.append(float(item.get("longitude", 0.0)))
            vels.append(float(item.get("velocity", 0.0)))
            alts.append(float(item.get("altitude", 0.0)))

        # Media (bucle manual)
        total_vel = 0.0
        for v in vels:
            total_vel += v
        avg_vel = total_vel / len(vels) if vels else 0.0

        # Min/Max (ordenar copia completa)
        vels_sorted = list(vels)
        vels_sorted.sort()
        min_vel = vels_sorted[0] if vels_sorted else 0.0
        max_vel = vels_sorted[-1] if vels_sorted else 0.0

        # Distancia total en ventana: recalcular desde cero en cada update
        total_km = 0.0
        coords = list(zip(lats, lons))
        for i in range(1, len(coords)):
            lat1, lon1 = coords[i - 1]
            lat2, lon2 = coords[i]
            total_km += haversine_km(lat1, lon1, lat2, lon2)

        last_lat = lats[-1] if lats else 0.0
        last_lon = lons[-1] if lons else 0.0
        last_vel = vels[-1] if vels else 0.0
        last_alt = alts[-1] if alts else 0.0

        return [
            f"Latitud: {last_lat:.5f}",
            f"Longitud: {last_lon:.5f}",
            f"Velocidad: {last_vel:.2f} km/h",
            f"Altitud: {last_alt:.2f} km",
            f"Velocidad media (ventana): {avg_vel:.2f} km/h",
            f"Min/Max velocidad (ventana): {min_vel:.2f} / {max_vel:.2f} km/h",
            f"Distancia aprox. (ventana): {total_km:.2f} km",
        ]

    def _on_help(self) -> None:
        show_help_dialog(
            self,
            "Help — Versión NO optimizada",
            [fetch_iss_payload, payload_to_sample, haversine_km, SlowPanel.process_payload],
        )


class FastPanel(PanelBase):
    """Versión optimizada (menos recorridos y estructuras adecuadas)."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, title="Versión optimizada", plot_color="#1f77b4")
        self.history: deque[IssSample] = deque(maxlen=HISTORY_SIZE)
        self._sum_vel: float = 0.0
        self._total_km_window: float = 0.0

    def process_payload(self, payload: dict) -> list[str]:
        """Procesa datos con menos recorridos y estructuras adecuadas.

        Optimizaciones:
        - Convertir una vez a un tipo compacto (IssSample)
        - Usar deque con maxlen
        - Usar sum/min/max con generadores
        - Mantener suma acumulada y distancia incremental (en vez de recalcular todo)
        """

        sample = payload_to_sample(payload)

        # Actualizar suma acumulada y distancia en ventana
        if self.history:
            prev = self.history[-1]
            self._total_km_window += haversine_km(prev.latitude, prev.longitude, sample.latitude, sample.longitude)

        if len(self.history) == self.history.maxlen:
            # Cuando el deque expulsa el elemento más viejo, hay que ajustar suma.
            # Para mantener el ejemplo simple (1º DAW), recalculamos solo la suma.
            # La distancia de ventana la dejamos como aproximación local.
            oldest = self.history[0]
            self._sum_vel -= oldest.velocity

        self.history.append(sample)
        self._sum_vel += sample.velocity

        n = len(self.history)
        avg_vel = (self._sum_vel / n) if n else 0.0
        min_vel = min((s.velocity for s in self.history), default=0.0)
        max_vel = max((s.velocity for s in self.history), default=0.0)

        return [
            f"Latitud: {sample.latitude:.5f}",
            f"Longitud: {sample.longitude:.5f}",
            f"Velocidad: {sample.velocity:.2f} km/h",
            f"Altitud: {sample.altitude:.2f} km",
            f"Velocidad media (ventana): {avg_vel:.2f} km/h",
            f"Min/Max velocidad (ventana): {min_vel:.2f} / {max_vel:.2f} km/h",
            f"Distancia aprox. (ventana): {self._total_km_window:.2f} km",
        ]

    def _on_help(self) -> None:
        show_help_dialog(
            self,
            "Help — Versión optimizada",
            [fetch_iss_payload, payload_to_sample, IssSample, haversine_km, FastPanel.process_payload],
        )


class App(tk.Tk):
    """Aplicación principal: divide la ventana en dos paneles y actualiza datos."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Actividad 5_3 — Optimización vs No optimización")
        self.geometry("1200x700")

        container = tk.Frame(self, padx=10, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        self.panel_left = SlowPanel(container)
        self.panel_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.panel_right = FastPanel(container)
        self.panel_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self._last_payload: dict | None = None
        self._demo = DemoIssSimulator()
        self._net_failures = 0
        self._net_backoff_until = 0.0
        self._schedule_next()

    def _schedule_next(self) -> None:
        self.after(UPDATE_MS, self._tick)

    def _tick(self) -> None:
        """Hace una actualización: descarga 1 payload y alimenta ambos paneles."""

        now = time.monotonic()
        if now < self._net_backoff_until:
            payload = self._last_payload or self._demo.next_payload()
            self._last_payload = payload
            self.panel_left.update_from_payload(payload)
            self.panel_right.update_from_payload(payload)
            self.panel_left._set_warn("sin conexión (modo DEMO)")
            self.panel_right._set_warn("sin conexión (modo DEMO)")
            self._schedule_next()
            return

        try:
            payload = fetch_iss_payload(timeout_s=2.0)
            self._last_payload = payload
            self._net_failures = 0
            self._net_backoff_until = 0.0
            self.panel_left.update_from_payload(payload)
            self.panel_right.update_from_payload(payload)
        except URLError as exc:
            self._net_failures += 1
            cooldown = min(60.0, 2.0 * (2 ** min(self._net_failures, 5)))  # 4,8,16,32,60...
            self._net_backoff_until = time.monotonic() + cooldown

            payload = self._last_payload or self._demo.next_payload()
            self._last_payload = payload
            self.panel_left.update_from_payload(payload)
            self.panel_right.update_from_payload(payload)

            msg = "sin conexión (modo DEMO)"
            self.panel_left._set_warn(msg)
            self.panel_right._set_warn(msg)
        except Exception as exc:  # noqa: BLE001
            msg = f"Error: {exc}"
            self.panel_left._set_error(msg)
            self.panel_right._set_error(msg)
        finally:
            self._schedule_next()


def main() -> int:
    """Punto de entrada del programa."""

    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
