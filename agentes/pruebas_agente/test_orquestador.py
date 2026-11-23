from pathlib import Path

import pytest

from agentes.orquestador import Orquestador, RevisorSoloLectura

REPO = Path(__file__).resolve().parents[2]

DEFECTO = 'def contar(votos):\n    return {"validos": len(votos), "blancos": votos.count(None)}\n'
CORRECCION = '''def contar(votos):
    validos = 0
    blancos = 0
    for voto in votos:
        if voto is None:
            blancos += 1
        else:
            validos += 1
    return {"validos": validos, "blancos": blancos}
'''


def test_revisor_no_edita():
    orch = Orquestador(REPO, aprobar_edicion=lambda *_: True)
    res = orch.ejecutar_variante_b(DEFECTO, CORRECCION)
    sandbox = res["sandbox"]
    revisor = RevisorSoloLectura(sandbox)
    with pytest.raises(PermissionError):
        revisor.editar("x", "y", "z")
    revisor.cerrar() if hasattr(revisor, "cerrar") else None
    sandbox.cerrar()


def test_variante_b_aprueba_en_una_ronda():
    orch = Orquestador(REPO, max_rondas=2, aprobar_edicion=lambda *_: True)
    res = orch.ejecutar_variante_b(DEFECTO, CORRECCION)
    assert res["veredicto"] == "APROBADO"
    assert res["rondas"] == 1
    res["sandbox"].cerrar()


def test_variante_b_maximo_dos_rondas():
    orch = Orquestador(REPO, max_rondas=5)
    assert orch.max_rondas == 2
