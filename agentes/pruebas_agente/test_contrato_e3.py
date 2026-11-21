"""Casos inválidos nuevos para el contrato (E3)."""

import json
from pathlib import Path
import tempfile

import pytest

from jsonschema import ValidationError
from agentes.agente.contrato import validar
from agentes.agente.herramientas import Sandbox
from agentes.agente.nucleo import ejecutar
from agentes.agente.politica import EDITABLE, LECTURAS


@pytest.mark.parametrize("respuesta", [
    '{"motivo":"x","accion":"leer_archivo","args":{},"respuesta":"","extra":1}',
    '{"motivo":"x","accion":"leer_archivo","args":"tests/test_issue_01.py","respuesta":""}',
    '{"motivo":"x","accion":"","args":{},"respuesta":""}',
    '{"motivo":"x","accion":"leer_archivo","args":{},"respuesta":123}',
    '{"motivo":"x","accion":"accion_desconocida","args":{},"respuesta":""}',
    '{"motivo":"x","accion":"editar_archivo","args":{"ruta":"agentes/demo/codigos.py","anterior":"a","nuevo":"b","extra":"z"},"respuesta":""}',
    '{"motivo":"x","accion":"ejecutar_pruebas","args":{"ruta":"x"},"respuesta":""}',
])
def test_rechaza_decisiones_invalidas_e3(respuesta):
    with pytest.raises((ValueError, ValidationError)):
        validar(respuesta)


def test_rechazo_no_ejecuta_herramienta(tmp_path):
    repo = Path(__file__).resolve().parents[2]

    class ModeloInvalido:
        def decidir(self, texto):
            return '{"motivo":"x","accion":"leer_archivo","args":{"ruta":"tests/test_issue_01.py","nuevo":"x"},"respuesta":""}'

    sandbox = Sandbox(repo)
    try:
        sesion = tmp_path / "sesion-e3"
        llamadas = {"n": 0}
        original = sandbox.ejecutar

        def contar(accion, args):
            llamadas["n"] += 1
            return original(accion, args)

        sandbox.ejecutar = contar
        resultado = ejecutar(ModeloInvalido(), sandbox, sesion, max_pasos=1)
        eventos = [json.loads(linea) for linea in (sesion / "traza.jsonl").read_text(encoding="utf-8").splitlines()]
        assert any(e["tipo"] == "rechazo" for e in eventos)
        assert llamadas["n"] == 0
        assert resultado == "Límite de pasos alcanzado."
    finally:
        sandbox.cerrar()
