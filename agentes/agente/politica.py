"""Política local de ISSUE-01, rutas exactas y Python de demostración acotado."""

import ast


EDITABLE = "agentes/demo/codigos.py"
LECTURAS = {EDITABLE, "issues/ISSUE-01.md", "tests/test_issue_01.py"}
NODOS = (
    ast.Module, ast.ClassDef, ast.FunctionDef, ast.arguments, ast.arg, ast.Assign,
    ast.Expr, ast.Constant, ast.Name, ast.Load, ast.Store, ast.Attribute,
    ast.Tuple, ast.Call, ast.If, ast.Compare, ast.In, ast.Return,
)


def ruta_segura(raiz, ruta):
    if ruta not in LECTURAS:
        raise ValueError("Ruta fuera de los archivos permitidos.")
    destino = raiz / ruta
    for padre in (destino, *destino.parents):
        if padre.is_symlink() or padre.is_junction():
            raise ValueError("Se rechazan enlaces y junctions.")
        if padre == raiz:
            break
    destino.resolve().relative_to(raiz.resolve())
    return destino


def validar_codigo(texto):
    arbol = ast.parse(texto)
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, NODOS):
            raise ValueError(f"Construcción Python fuera de la demostración: {type(nodo).__name__}.")
        if isinstance(nodo, ast.Attribute) and nodo.attr not in ("participaciones", "add", "lower", "casefold"):
            raise ValueError("Atributo fuera de la demostración.")
        if isinstance(nodo, (ast.ClassDef, ast.FunctionDef)) and nodo.decorator_list:
            raise ValueError("Decoradores no permitidos.")
        if isinstance(nodo, ast.Call):
            validar_llamada(nodo)


def validar_llamada(nodo):
    nombre = ast.unparse(nodo.func)
    permitidas = {"set", "self.participaciones.add", "codigo.lower", "codigo.casefold"}
    if nombre not in permitidas or nodo.keywords:
        raise ValueError(f"Llamada no permitida: {nombre}.")
