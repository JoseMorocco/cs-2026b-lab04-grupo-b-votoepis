"""Comprobación AST complementaria local de los contratos de import-linter.

Permite demostrar fallas estructurales sin depender de importar o ejecutar
los módulos; el CI ejecuta *también* import-linter.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src/votacion"


def dependencias_de(nombre):
    archivo = ROOT / f"{nombre}.py"
    imports = set()
    for nodo in ast.walk(ast.parse(archivo.read_text(encoding="utf-8"))):
        if isinstance(nodo, ast.Import):
            imports.update(a.name for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            imports.add(nodo.module)
    return imports


def test_ff01_dominio_no_importa_infraestructura():
    prohibidos = {f"src.votacion.{nombre}" for nombre in
                   ("externos", "servicio", "eventos", "elegibilidad",
                    "decoradores", "ia")}
    assert not (dependencias_de("dominio") & prohibidos)


def test_ff02_adaptadores_no_importan_servicio():
    for modulo in ("elegibilidad", "decoradores", "eventos", "externos"):
        assert "src.votacion.servicio" not in dependencias_de(modulo), modulo
