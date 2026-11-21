"""Contrato estructural y argumentos por herramienta."""

import json
from pathlib import Path

from jsonschema import Draft7Validator


VALIDADOR = Draft7Validator(json.loads(Path(__file__).with_name("contrato.json").read_bytes()))
ARGUMENTOS = {
    "leer_archivo": {"ruta"},
    "editar_archivo": {"ruta", "anterior", "nuevo"},
    "ejecutar_pruebas": set(),
    "ver_cambios": set(),
    "mapa_repo": set(),
    "anotar": {"texto"},
    "leer_notas": set(),
    "final": set(),
}


def objeto_sin_duplicados(pares):
    resultado = {}
    for clave, valor in pares:
        if clave in resultado:
            raise ValueError(f"Clave JSON duplicada: {clave}.")
        resultado[clave] = valor
    return resultado


def validar(texto):
    decision = json.loads(texto, object_pairs_hook=objeto_sin_duplicados)
    VALIDADOR.validate(decision)
    if set(decision["args"]) != ARGUMENTOS[decision["accion"]]:
        raise ValueError("Argumentos incorrectos para la acción.")
    if decision["accion"] == "final" and not decision["respuesta"].strip():
        raise ValueError("La decisión final requiere una respuesta.")
    if decision["accion"] != "final" and decision["respuesta"]:
        raise ValueError("Solo la decisión final lleva respuesta.")
    return decision
