"""Generador de documentación externa (HTML y TXT) para la Actividad 5_3.

Este script carga el archivo `actividad5.3.py` y extrae docstrings para generar:
- Una página HTML con la documentación.
- Un TXT con la documentación.

Requisitos
---------
- Solo librería estándar (no necesitas instalar nada).

Ejecutar
--------
- python "Actividad 5/docgen_actividad5_3.py"

Salida
------
Se crean archivos en:
- Actividad 5/docs_actividad5_3/
"""

from __future__ import annotations

import html
import importlib.util
import inspect
import os
import sys
from pathlib import Path


def load_module_from_path(module_path: Path, module_name: str):
    """Carga un módulo Python desde una ruta de archivo."""

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar el módulo desde: {module_path}")
    mod = importlib.util.module_from_spec(spec)
    # Importante: registrar en sys.modules antes de exec_module.
    # Algunas librerías (p.ej. dataclasses) consultan sys.modules durante la carga.
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def collect_docs(mod) -> list[tuple[str, str]]:
    """Recoge docstrings de módulo, clases y funciones públicas."""

    items: list[tuple[str, str]] = []

    module_doc = inspect.getdoc(mod) or "(Sin docstring de módulo)"
    items.append(("Módulo", module_doc))

    for name, obj in sorted(mod.__dict__.items(), key=lambda kv: kv[0]):
        if name.startswith("_"):
            continue
        if inspect.isclass(obj) or inspect.isfunction(obj):
            # Solo documentar lo que está definido en el propio módulo.
            # Así evitamos docstrings de imports (stdlib) que suelen venir en inglés.
            if getattr(obj, "__module__", None) != getattr(mod, "__name__", None):
                continue
            doc = inspect.getdoc(obj)
            if doc:
                kind = "Clase" if inspect.isclass(obj) else "Función"
                items.append((f"{kind}: {name}", doc))

    return items


def write_html(out_path: Path, title: str, docs: list[tuple[str, str]]) -> None:
    """Genera una página HTML simple con la documentación."""

    parts: list[str] = []
    parts.append("<!doctype html>")
    parts.append('<html lang="es">')
    parts.append("<head>")
    parts.append('<meta charset="utf-8">')
    parts.append(f"<title>{html.escape(title)}</title>")
    parts.append(
        "<style>body{font-family:Segoe UI,Arial,sans-serif;margin:20px;}"
        "pre{background:#f6f6f6;padding:12px;border-radius:8px;overflow:auto;}"
        "h1{margin-top:0;}h2{margin-top:22px;}</style>"
    )
    parts.append("</head>")
    parts.append("<body>")
    parts.append(f"<h1>{html.escape(title)}</h1>")

    for heading, text in docs:
        parts.append(f"<h2>{html.escape(heading)}</h2>")
        parts.append(f"<pre>{html.escape(text)}</pre>")

    parts.append("</body></html>")
    out_path.write_text("\n".join(parts), encoding="utf-8")


def write_txt(out_path: Path, title: str, docs: list[tuple[str, str]]) -> None:
    """Genera un TXT con la documentación (UTF-8)."""

    lines: list[str] = [title, "=" * len(title), ""]
    for heading, text in docs:
        lines.append(heading)
        lines.append("-" * len(heading))
        lines.append(text)
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    """Entry point del generador de documentación."""

    root = Path(__file__).resolve().parent
    module_path = root / "actividad5.3.py"
    out_dir = root / "docs_actividad5_3"
    out_dir.mkdir(parents=True, exist_ok=True)

    mod = load_module_from_path(module_path, "actividad5_3")
    docs = collect_docs(mod)

    title = "Actividad 5_3 — Documentación"
    html_path = out_dir / "actividad5.3_documentacion.html"
    txt_path = out_dir / "actividad5.3_documentacion.txt"

    write_html(html_path, title, docs)
    print(f"OK HTML: {html_path}")

    write_txt(txt_path, title, docs)
    print(f"OK TXT: {txt_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
