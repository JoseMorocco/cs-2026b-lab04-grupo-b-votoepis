"""Integración pública con grabaciones y procedencia, sin llamadas de red."""

import json
from pathlib import Path

import pytest
import yaml

from prompts import proveedor_grabado
from prompts.criterios import gestionar_grabaciones
from prompts.criterios.aserciones import contrato
from prompts.criterios.renderizar_iteraciones import prompt_v2, prompt_v3
from prompts.criterios.renderizar_prompt import prompt_v1
from src.votacion.generador_criterios import GeneradorCriterios
from src.votacion.ia import ProveedorLLM


CRITERIOS = Path(__file__).resolve().parents[1] / "prompts" / "criterios"
RENDERIZADORES = {"v1": prompt_v1, "v2": prompt_v2, "v3": prompt_v3}
CASOS = yaml.safe_load((CRITERIOS / "casos.yaml").read_text(encoding="utf-8"))


class ProveedorGrabado(ProveedorLLM):
    def __init__(self, version, variables):
        self.version = version
        self.variables = variables
        self.prompts = []
        self.respuestas = []

    def completar(self, prompt):
        self.prompts.append(prompt)
        resultado = proveedor_grabado.call_api(
            prompt, {"config": {"version": self.version}}, {"vars": self.variables}
        )
        if "error" in resultado:
            raise ValueError(resultado["error"])
        self.respuestas.append(resultado["output"])
        return resultado["output"]


@pytest.mark.parametrize("version", ["v1", "v2", "v3"])
@pytest.mark.parametrize("historia_id", ["HU-01", "LAB09-AMB"])
def test_acepta_grabacion_valida_con_plantilla_versionada(version, historia_id):
    variables = next(c["vars"] for c in CASOS if c["vars"]["historia_id"] == historia_id)
    proveedor = ProveedorGrabado(version, variables)
    carpeta = CRITERIOS / "grabaciones" / version
    archivos = [carpeta / f"{historia_id}.txt", carpeta / "procedencia.json"]
    originales = [archivo.read_bytes() for archivo in archivos]

    resultado = GeneradorCriterios(proveedor, version=version).generar(
        historia_id, variables["historia"]
    )

    assert resultado == json.loads(originales[0])
    assert proveedor.prompts == [RENDERIZADORES[version]({"vars": variables})]
    assert proveedor.prompts[0].endswith("\n")
    assert [respuesta.encode("utf-8") for respuesta in proveedor.respuestas] == [originales[0]]
    assert [archivo.read_bytes() for archivo in archivos] == originales


@pytest.mark.parametrize("respuesta", [
    b'{"historia_id":"HU-01","invest_ok":true,"preguntas":[],"escenarios":[]}\r\n',
    b'{"historia_id":"HU-01","invest_ok":false,"preguntas":[],"escenarios":[]}\n',
    b'{"historia_id":"OTRA","invest_ok":false,"preguntas":["Que falta?"],"escenarios":[]}\n',
    b'```json\n{"historia_id":"HU-01"}\n```\n',
])
def test_rechaza_grabacion_invalida_sin_repararla(tmp_path, monkeypatch, respuesta):
    variables = CASOS[0]["vars"]
    carpeta = tmp_path / "v1"
    carpeta.mkdir()
    manifiesto = carpeta / "procedencia.json"
    fuente = tmp_path / "respuesta.txt"
    fuente.write_bytes(respuesta)
    monkeypatch.setattr(gestionar_grabaciones, "CARPETA", carpeta)
    monkeypatch.setattr(gestionar_grabaciones, "MANIFIESTO", manifiesto)
    monkeypatch.setattr(proveedor_grabado, "GRABACIONES", tmp_path)
    gestionar_grabaciones.registrar(variables, fuente, "Proveedor de prueba", "grabado")
    original = manifiesto.read_bytes()
    proveedor = ProveedorGrabado("v1", variables)
    motivo = contrato(respuesta.decode("utf-8"), {"vars": variables})["reason"]

    with pytest.raises(ValueError) as error:
        GeneradorCriterios(proveedor).generar(variables["historia_id"], variables["historia"])

    assert str(error.value) == motivo
    assert proveedor.prompts == [prompt_v1({"vars": variables})]
    assert [texto.encode("utf-8") for texto in proveedor.respuestas] == [respuesta]
    assert (carpeta / "HU-01.txt").read_bytes() == respuesta
    assert fuente.read_bytes() == respuesta
    assert manifiesto.read_bytes() == original


def test_rechaza_version_desconocida_sin_invocar_proveedor():
    proveedor = ProveedorGrabado("v1", CASOS[0]["vars"])
    with pytest.raises(ValueError, match="^Versión de criterios no soportada: v4$"):
        GeneradorCriterios(proveedor, version="v4")
    assert proveedor.prompts == []
    assert proveedor.respuestas == []


def test_propaga_error_de_procedencia_sin_validar_otra_respuesta():
    variables = dict(CASOS[0]["vars"], historia="Historia modificada")
    proveedor = ProveedorGrabado("v1", variables)
    with pytest.raises(ValueError, match=r"^El prompt no coincide con la procedencia de v1/HU-01\.$"):
        GeneradorCriterios(proveedor).generar(variables["historia_id"], variables["historia"])
    assert proveedor.prompts == [prompt_v1({"vars": variables})]
    assert proveedor.respuestas == []
