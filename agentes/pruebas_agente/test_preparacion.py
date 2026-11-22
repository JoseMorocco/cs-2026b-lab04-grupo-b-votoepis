"""Verificaciones de infraestructura. Las decisiones unitarias no son una ejecución de E2."""

from hashlib import sha256
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from agentes.agente.contrato import validar
from agentes.agente.herramientas import Sandbox
from agentes.agente.modelo import contexto
from agentes.agente.nucleo import ejecutar
from agentes.agente.politica import EDITABLE, LECTURAS, ruta_segura
from agentes.agente.traza import a_mermaid


REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def sandbox():
    originales = {ruta: (REPO / ruta).read_bytes() for ruta in LECTURAS}
    copia = Sandbox(REPO, aprobar_edicion=lambda *_: True)
    try:
        yield copia
    finally:
        copia.cerrar()
        for ruta, contenido in originales.items():
            assert (REPO / ruta).read_bytes() == contenido, f"El sandbox alteró el origen: {ruta}"


@pytest.fixture
def sandbox_con_defecto(sandbox):
    """Siembra ISSUE-01 solo en la copia, aunque el origen ya esté corregido."""
    actual = sandbox.leer_archivo(EDITABLE)
    defectuoso = "clave = (eleccion, codigo)"
    corregido = "clave = (eleccion, codigo.casefold())"
    assert actual.count(defectuoso) + actual.count(corregido) == 1
    sandbox.editar_archivo(EDITABLE, actual, actual.replace(corregido, defectuoso))
    return sandbox


@pytest.mark.parametrize("respuesta", [
    "texto libre",
    '{"motivo":"x","accion":"ejecutar_comando","args":{},"respuesta":""}',
    '{"motivo":"x","accion":"leer_archivo","args":{"ruta":"tests/test_issue_01.py","nuevo":"x"},"respuesta":""}',
    '{"motivo":"x","accion":"final","accion":"leer_archivo","args":{},"respuesta":""}',
])
def test_rechaza_decisiones_fuera_del_protocolo(respuesta):
    with pytest.raises((ValueError, ValidationError)):
        validar(respuesta)


@pytest.mark.parametrize("ruta", [
    "../tests/test_issue_01.py",
    "/etc/passwd",
    "agentes/demo/../../tests/test_issue_01.py",
    "src/votacion/servicio.py",
])
def test_rutas_exactas(sandbox, ruta):
    with pytest.raises(ValueError, match="permitidos"):
        ruta_segura(sandbox.raiz, ruta)


def test_edicion_y_pruebas_reales_solo_en_copia(sandbox_con_defecto):
    sandbox = sandbox_con_defecto
    fuente = REPO / EDITABLE
    previo = fuente.read_bytes()
    tests = (REPO / "tests/test_issue_01.py").read_bytes()
    diff_rojo = sandbox.ver_cambios()
    rojo = sandbox.ejecutar_pruebas()
    assert rojo["codigo"] == 1 and "assert True is False" in rojo["salida"]
    sandbox.editar_archivo(EDITABLE, "clave = (eleccion, codigo)", "clave = (eleccion, codigo.casefold())")
    verde = sandbox.ejecutar_pruebas()
    assert verde["codigo"] == 0 and "1 passed" in verde["salida"]
    assert "clave = (eleccion, codigo.casefold())" in sandbox.leer_archivo(EDITABLE)
    assert sandbox.ver_cambios() != diff_rojo
    assert fuente.read_bytes() == previo
    assert (REPO / "tests/test_issue_01.py").read_bytes() == tests


def test_protege_pruebas_y_rechaza_importaciones(sandbox_con_defecto):
    sandbox = sandbox_con_defecto
    codigo_previo = (sandbox.raiz / EDITABLE).read_bytes()
    prueba = sandbox.raiz / "tests/test_issue_01.py"
    prueba_previa = prueba.read_bytes()
    with pytest.raises(ValueError, match="Solo se permite"):
        sandbox.editar_archivo("tests/test_issue_01.py", "assert", "pass")
    assert prueba.read_bytes() == prueba_previa
    with pytest.raises(ValueError, match="Construcción Python"):
        sandbox.editar_archivo(EDITABLE, "clave = (eleccion, codigo)", "import os")
    assert (sandbox.raiz / EDITABLE).read_bytes() == codigo_previo
    prueba.write_text("def test_falso(): assert True", encoding="utf-8")
    with pytest.raises(ValueError, match="alterada"):
        sandbox.ejecutar_pruebas()


def test_rechaza_enlace_fuera_de_copia(sandbox, tmp_path):
    permitido = sandbox.raiz / EDITABLE
    permitido.unlink()
    ajeno = tmp_path / "ajeno.py"
    ajeno.write_text("secreto", encoding="utf-8")
    try:
        permitido.symlink_to(ajeno)
    except OSError:
        pytest.skip("El sistema no permite crear symlinks para esta prueba.")
    with pytest.raises(ValueError, match="enlaces"):
        sandbox.leer_archivo(EDITABLE)


def test_rechazos_consumen_presupuesto_y_se_graban_intactos(sandbox, tmp_path):
    class ModeloUnitario:
        def decidir(self, texto):
            assert json.loads(texto)["historial"]
            return " ```json\n{}\n``` "

    sesion = tmp_path / "sesion-unitaria"
    resultado = ejecutar(ModeloUnitario(), sandbox, sesion, max_pasos=2)
    assert resultado == "Límite de pasos alcanzado."
    eventos = [json.loads(linea) for linea in (sesion / "traza.jsonl").read_text(encoding="utf-8").splitlines()]
    assert sum(e["tipo"] == "rechazo" for e in eventos) == 2
    bruto = (sesion / "decision-01.txt").read_bytes()
    respuesta = next(e for e in eventos if e["tipo"] == "respuesta")
    assert sha256(bruto).hexdigest() == respuesta["sha256"]
    assert bruto == b" ```json\n{}\n``` "
    assert (sesion / "trayectoria.mmd").read_text(encoding="utf-8") == a_mermaid(eventos)
    assert eventos[-1]["estado"] == "DETENIDO"


def test_contexto_incluye_protocolo():
    datos = json.loads(contexto([{"rol": "objetivo", "texto": "ISSUE-01"}]))
    assert datos["contrato"]["required"] == ["motivo", "accion", "args", "respuesta"]
    assert set(datos["herramientas"]) == {
        "leer_archivo", "editar_archivo", "ejecutar_pruebas", "ver_cambios",
        "mapa_repo", "anotar", "leer_notas", "final",
    }
