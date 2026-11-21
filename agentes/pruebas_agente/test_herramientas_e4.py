import pytest
from pathlib import Path

from agentes.agente.herramientas import Sandbox
from agentes.agente.politica import ISSUE_CONFIG

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def sandbox():
    s = Sandbox(REPO, issue="ISSUE-03")
    try:
        yield s
    finally:
        s.cerrar()


def test_mapa_repo_contiene_archivo_y_firma(sandbox):
    resultado = sandbox.mapa_repo()
    assert "cierre.py" in resultado
    assert "puede_cerrar" in resultado


def test_notas_persisten(sandbox):
    sandbox.anotar("hipótesis: comparar instantes")
    assert "hipótesis" in sandbox.leer_notas()


def test_nota_invalida(sandbox):
    with pytest.raises(ValueError):
        sandbox.anotar("")
    with pytest.raises(ValueError):
        sandbox.anotar("x" * 3000)


def test_no_escribe_fuera_sandbox(sandbox, tmp_path):
    origen = REPO / "agentes/demo/cierre.py"
    previo = origen.read_bytes()
    sandbox.anotar("nota")
    assert origen.read_bytes() == previo


def test_ruta_protegida_issue03(sandbox):
    with pytest.raises(ValueError, match="permitidos"):
        sandbox.leer_archivo("src/votacion/servicio.py")
