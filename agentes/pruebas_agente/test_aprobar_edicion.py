"""Pruebas de aprobación humana del ejecutor (E6)."""

import json
from pathlib import Path
from io import StringIO

import pytest

from agentes.agente.herramientas import Sandbox
from agentes.agente.nucleo import procesar_decision
from agentes.agente.politica import EDITABLE, aprobar_edicion


REPO = Path(__file__).resolve().parents[2]
ANTERIOR = "clave = (eleccion, codigo.casefold())"
NUEVO = "clave = (eleccion, codigo)"


@pytest.fixture
def sandbox():
    instancia = Sandbox(REPO)
    try:
        yield instancia
    finally:
        instancia.cerrar()


def test_pide_aprobacion_para_cada_edicion(monkeypatch, sandbox):
    respuestas = iter(["s", "s"])
    prompts = []

    def leer_respuesta(prompt):
        prompts.append(prompt)
        return next(respuestas)

    monkeypatch.setattr("builtins.input", leer_respuesta)

    sandbox.editar_archivo(EDITABLE, ANTERIOR, NUEVO)
    sandbox.editar_archivo(EDITABLE, NUEVO, ANTERIOR)

    assert len(prompts) == 2


def test_solo_acepta_s_o_n_y_rechaza_sin_escribir(monkeypatch, sandbox):
    respuestas = iter(["quizá", "n"])
    prompts = []

    def leer_respuesta(prompt):
        prompts.append(prompt)
        return next(respuestas)

    monkeypatch.setattr("builtins.input", leer_respuesta)
    archivo = sandbox.raiz / EDITABLE
    antes = archivo.read_bytes()

    with pytest.raises(PermissionError, match="rechaz"):
        sandbox.editar_archivo(EDITABLE, ANTERIOR, NUEVO)

    assert len(prompts) == 2
    assert archivo.read_bytes() == antes


@pytest.mark.parametrize("respuesta", ["", "S", "N", "si", "yes", " s ", "\tn\t"])
def test_aprobar_edicion_repite_hasta_recibir_token_exacto(respuesta):
    respuestas = iter([respuesta, "n"])
    prompts = []

    def leer_respuesta(prompt):
        prompts.append(prompt)
        return next(respuestas)

    assert aprobar_edicion("agentes/demo/codigos.py", "antes", "después", leer_respuesta) is False
    assert len(prompts) == 2


@pytest.mark.parametrize(
    ("respuesta", "estado_aprobacion", "estado_herramienta"),
    [
        ("s", "APROBADA", "OBSERVANDO"),
        ("n", "RECHAZADA", "BLOQUEADO"),
    ],
)
def test_traza_distingue_la_aprobacion_humana(
    monkeypatch, sandbox, respuesta, estado_aprobacion, estado_herramienta
):
    monkeypatch.setattr("builtins.input", lambda prompt: respuesta)
    decision = json.dumps({
        "motivo": "Aplicar una corrección revisada.",
        "accion": "editar_archivo",
        "args": {"ruta": EDITABLE, "anterior": ANTERIOR, "nuevo": NUEVO},
        "respuesta": "",
    })
    eventos = []
    procesar_decision(decision, sandbox, StringIO(), eventos, paso=1)

    assert any(
        evento["tipo"] == "aprobacion" and evento["estado"] == estado_aprobacion
        for evento in eventos
    )
    assert any(
        evento["tipo"] == "herramienta" and evento["estado"] == estado_herramienta
        for evento in eventos
    )


def test_eof_rechaza_la_edicion_y_registra_el_bloqueo(monkeypatch, sandbox):
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(EOFError))
    decision = json.dumps({"motivo": "Aplicar la corrección revisada.", "accion": "editar_archivo", "args": {"ruta": EDITABLE, "anterior": ANTERIOR, "nuevo": NUEVO}, "respuesta": ""})
    eventos = []

    resultado = procesar_decision(decision, sandbox, StringIO(), eventos, paso=1)

    assert resultado["resultado"]["aprobacion"] == "RECHAZADA"
    assert eventos[-2]["estado"] == "RECHAZADA"
    assert eventos[-1]["estado"] == "BLOQUEADO"
