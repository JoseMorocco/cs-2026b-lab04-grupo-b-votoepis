"""Entrada de consola del agente interactivo de ISSUE-01."""

import argparse
from pathlib import Path

from agentes.agente.herramientas import Sandbox
from agentes.agente.modelo import ModeloInteractivo, contexto
from agentes.agente.nucleo import ejecutar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sesion", type=Path)
    parser.add_argument("--contexto", action="store_true", help="Imprime el primer contexto sin ejecutar una sesión")
    args = parser.parse_args()
    origen = Path(__file__).resolve().parents[2]
    if args.contexto:
        issue = (origen / "issues/ISSUE-01.md").read_text(encoding="utf-8")
        print(contexto([{"rol": "objetivo", "texto": issue}]))
        return
    if args.sesion is None:
        parser.error("Indica --sesion con una carpeta nueva para preservar las evidencias.")
    sesion = args.sesion.resolve()
    # Las evidencias deben quedar fuera del sandbox temporal.
    if sesion.exists():
        parser.error("La carpeta de sesión ya existe.")
    sandbox = Sandbox(origen)
    try:
        print(ejecutar(ModeloInteractivo(), sandbox, sesion))
    finally:
        sandbox.cerrar()


if __name__ == "__main__":
    main()
