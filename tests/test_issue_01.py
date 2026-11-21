import pytest

from agentes.demo.codigos import RegistroPorCodigo


@pytest.mark.xfail(strict=True, reason="ISSUE-01 sembrado: código sensible a mayúsculas")
def test_issue_01_impide_doble_voto_por_cambio_de_mayusculas():
    registro = RegistroPorCodigo()
    assert registro.emitir("eleccion-A", "epis42") is True
    assert registro.emitir("eleccion-A", "EPIS42") is False
    assert len(registro.participaciones) == 1
    assert registro.emitir("eleccion-B", "EPIS42") is True
