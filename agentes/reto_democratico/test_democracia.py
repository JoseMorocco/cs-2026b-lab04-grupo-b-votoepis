"""Pruebas unitarias del reto. Los votos construidos aquí son datos de prueba."""

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from agentes.agente.herramientas import Sandbox
from agentes.reto_democratico.comparar import CORRECCION, DEFECTO, comparar, inventario
from agentes.reto_democratico.revision import (
    Expediente, RevisorCorreccion, RevisorDiseno, RevisorSeguridad, Voto, contar_votos,
)


REPO = Path(__file__).resolve().parents[2]
ROLES = ("correccion", "diseno", "seguridad")


@pytest.mark.parametrize("favorables,decision", [
    (3, "APROBADO"), (2, "APROBADO"), (1, "RECHAZADO"), (0, "RECHAZADO"),
])
def test_mayoria(favorables, decision):
    votos = [Voto(rol, "APROBADO" if i < favorables else "RECHAZADO",
                  ("Motivo unitario.",), ()) for i, rol in enumerate(ROLES)]
    resultado = contar_votos(votos)
    assert resultado["decision"] == decision
    assert resultado["favorables"] == favorables
    assert resultado["rechazos"] == 3 - favorables


def test_no_cuenta_votos_duplicados_o_incompletos():
    voto = Voto("correccion", "APROBADO", ("Motivo unitario.",), ())
    with pytest.raises(ValueError, match="cada uno"):
        contar_votos([voto, voto, voto])
    with pytest.raises(ValueError, match="cada uno"):
        contar_votos([voto])
    with pytest.raises(ValueError, match="inválido"):
        Voto("seguridad", "ABSTENCION", ("Motivo unitario.",), ())


@pytest.fixture
def datos():
    return Expediente(DEFECTO, CORRECCION, "diff unitario", '{"codigo":0}',
                      ("agentes/demo/conteo.py",), "agentes/demo/conteo.py")


def test_revisiones_independientes_y_expediente_inmutable(datos):
    revisores = (RevisorCorreccion(), RevisorDiseno(), RevisorSeguridad())
    orden_directo = [r.revisar(datos) for r in revisores]
    inverso = [r.revisar(datos) for r in reversed(revisores)]
    assert orden_directo == list(reversed(inverso))
    assert {v.revisor for v in orden_directo} == set(ROLES)
    assert all(v.voto == "APROBADO" and v.motivos and v.hallazgos for v in orden_directo)
    with pytest.raises(FrozenInstanceError):
        datos.propuesto = DEFECTO


@pytest.mark.parametrize("revisor", [RevisorCorreccion(), RevisorDiseno(), RevisorSeguridad()])
def test_revisores_no_pueden_editar(revisor):
    with pytest.raises(PermissionError, match="solo lectura"):
        revisor.editar("tests/test_issue_02.py", "assert", "pass")
    assert not hasattr(revisor, "sandbox")


def test_especialistas_detectan_sus_problemas(datos):
    assert RevisorCorreccion().revisar(replace(datos, pruebas_json='{"codigo":1}')).voto == "RECHAZADO"
    assert RevisorDiseno().revisar(replace(datos, propuesto="def otra(): return 0")).voto == "RECHAZADO"
    cambio_tests = replace(datos, archivos_cambiados=("tests/test_issue_02.py",))
    voto = RevisorSeguridad().revisar(cambio_tests)
    assert voto.voto == "RECHAZADO"
    assert any("tests/test_issue_02.py" in motivo for motivo in voto.motivos)
    assert RevisorSeguridad().revisar(replace(datos, propuesto="import os")).voto == "RECHAZADO"


def test_sandbox_rechaza_tests_e_importaciones_y_preserva_origen():
    origen = REPO / "tests/test_issue_02.py"
    original = origen.read_bytes()
    sandbox = Sandbox(REPO, issue="ISSUE-02")
    try:
        codigo = sandbox.leer_archivo(sandbox.editable)
        with pytest.raises(ValueError, match="Solo se permite"):
            sandbox.editar_archivo("tests/test_issue_02.py", "assert", "pass")
        with pytest.raises(ValueError, match="Construcción Python"):
            sandbox.editar_archivo(sandbox.editable, codigo, "import os\n")
        assert sandbox.leer_archivo(sandbox.editable) == codigo
        assert (sandbox.raiz / sandbox.prueba).read_bytes() == original
    finally:
        sandbox.cerrar()
    assert origen.read_bytes() == original


def test_comparacion_real_preserva_fuentes_y_mismo_cambio():
    rutas = {"agentes/demo/conteo.py", "issues/ISSUE-02.md", "tests/test_issue_02.py"}
    antes = inventario(REPO, rutas)
    resultado = comparar(REPO)
    assert antes == inventario(REPO, rutas)
    individual, democratica = resultado["individual"], resultado["democratica"]
    assert individual["diff"] == democratica["diff"]
    assert individual["codigo_propuesto"] == democratica["codigo_propuesto"]
    assert individual["pruebas"]["codigo"] == democratica["pruebas"]["codigo"] == 0
    assert democratica["resultado"]["favorables"] == 3
    assert individual["resultado"]["decision"] == democratica["resultado"]["decision"] == "APROBADO"
    assert individual["revision_sin_escrituras"] and democratica["revision_sin_escrituras"]
    assert individual["total_operaciones"] == 5 and democratica["total_operaciones"] == 7
    assert democratica["tokens_medidos"] is None
