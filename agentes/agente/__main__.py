"""Entrada de consola del agente interactivo."""

import argparse
from pathlib import Path

from agentes.agente.herramientas import Sandbox
from agentes.agente.modelo import ModeloInteractivo, contexto
from agentes.agente.nucleo import ejecutar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sesion", type=Path)
    parser.add_argument("--contexto", action="store_true", help="Imprime el primer contexto sin ejecutar una sesión")
    parser.add_argument("--issue", default="ISSUE-01", help="Issue a resolver (ISSUE-01, ISSUE-02, ISSUE-03)")
    args = parser.parse_args()
    origen = Path(__file__).resolve().parents[2]
    if args.contexto:
        issue_path = f"issues/{args.issue}.md" if not args.issue.startswith("issues/") else args.issue
        issue = (origen / issue_path).read_text(encoding="utf-8")
        print(contexto([{"rol": "objetivo", "texto": issue}]))
        return
    if args.sesion is None:
        parser.error("Indica --sesion con una carpeta nueva para preservar las evidencias.")
    sesion = args.sesion.resolve()
    if sesion.exists():
        parser.error("La carpeta de sesión ya existe.")
    sandbox = Sandbox(origen, issue=args.issue)
    try:
        print(ejecutar(ModeloInteractivo(), sandbox, sesion))
    finally:
        sandbox.cerrar()


if __name__ == "__main__":
    main()
