from agentes.demo.conteo import contar


def test_issue_02_separa_blancos_de_validos():
    assert contar(["candidato-A", None, "candidato-B"]) == {"validos": 2, "blancos": 1}
