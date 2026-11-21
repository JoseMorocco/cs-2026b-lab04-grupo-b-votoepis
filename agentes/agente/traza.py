"""Conversión determinista de eventos reales a un diagrama Mermaid."""

import argparse
import json
from pathlib import Path


def a_mermaid(eventos):
    lineas = ["flowchart TD"]
    for indice, evento in enumerate(eventos):
        etiqueta = f"{evento['estado']} · {evento['tipo']}"
        if "accion" in evento:
            etiqueta += f" · {evento['accion']}"
        lineas.append(f'    n{indice}["{etiqueta}"]')
        if indice:
            lineas.append(f"    n{indice-1} --> n{indice}")
    return "\n".join(lineas) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("traza", type=Path)
    parser.add_argument("salida", type=Path)
    args = parser.parse_args()
    eventos = [json.loads(linea) for linea in args.traza.read_text(encoding="utf-8").splitlines()]
    with args.salida.open("x", encoding="utf-8", newline="\n") as salida:
        salida.write(a_mermaid(eventos))


if __name__ == "__main__":
    main()
