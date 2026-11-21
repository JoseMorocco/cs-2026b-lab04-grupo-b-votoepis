"""Política local de issues de demostración, rutas exactas y Python acotado."""

import ast


ISSUE_CONFIG = {
    "ISSUE-01": {
        "editable": "agentes/demo/codigos.py",
        "lecturas": {"agentes/demo/codigos.py", "issues/ISSUE-01.md", "tests/test_issue_01.py"},
        "prueba": "tests/test_issue_01.py",
        "issue": "issues/ISSUE-01.md",
    },
    "ISSUE-02": {
        "editable": "agentes/demo/conteo.py",
        "lecturas": {"agentes/demo/conteo.py", "issues/ISSUE-02.md", "tests/test_issue_02.py"},
        "prueba": "tests/test_issue_02.py",
        "issue": "issues/ISSUE-02.md",
    },
    "ISSUE-03": {
        "editable": "agentes/demo/cierre.py",
        "lecturas": {"agentes/demo/cierre.py", "issues/ISSUE-03.md", "tests/test_issue_03.py"},
        "prueba": "tests/test_issue_03.py",
        "issue": "issues/ISSUE-03.md",
    },
}

# Compatibilidad con el prototipo original de ISSUE-01.
EDITABLE = ISSUE_CONFIG["ISSUE-01"]["editable"]
LECTURAS = set(ISSUE_CONFIG["ISSUE-01"]["lecturas"])
NODOS = (
    ast.Module, ast.ClassDef, ast.FunctionDef, ast.arguments, ast.arg, ast.Assign,
    ast.AugAssign, ast.Expr, ast.Constant, ast.Name, ast.Load, ast.Store, ast.Attribute,
    ast.Tuple, ast.Call, ast.If, ast.For, ast.Compare, ast.In, ast.Is, ast.Return,
    ast.Dict,
    ast.Eq, ast.NotEq, ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.IsNot,
)


def ruta_segura(raiz, ruta, permitidos=None):
    if permitidos is None:
        permitidos = LECTURAS
    if ruta not in permitidos:
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
