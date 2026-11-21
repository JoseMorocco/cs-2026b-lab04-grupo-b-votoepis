import pytest

from agentes.demo.conteo import contar


@pytest.mark.xfail(strict=True, reason="ISSUE-02 sembrado: blancos incluidos como válidos")
def test_issue_02_separa_blancos_de_validos():
    assert contar(["candidato-A", None, "candidato-B"]) == {"validos": 2, "blancos": 1}
