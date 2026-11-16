import json
from pathlib import Path
import re

import pytest
import yaml
from jsonschema import Draft7Validator


CRITERIOS = Path(__file__).resolve().parent
REPO = CRITERIOS.parents[1]
ESQUEMA = json.loads((CRITERIOS / "esquema.json").read_text(encoding="utf-8"))
CASOS = yaml.safe_load((CRITERIOS / "casos.yaml").read_text(encoding="utf-8"))
ESCENARIO = {
    "titulo": "Voto registrado",
    "tipo": "exito",
    "dado": ["Una elección abierta"],
    "cuando": "El estudiante confirma su voto",
    "entonces": ["El voto queda registrado"],
}


def test_esquema_y_salidas_validas():
    Draft7Validator.check_schema(ESQUEMA)
    validator = Draft7Validator(ESQUEMA)
    validator.validate(dict(historia_id="HU-01", invest_ok=True, preguntas=[],
                            escenarios=[ESCENARIO]))
    validator.validate(dict(historia_id="LAB09-AMB", invest_ok=False,
                            preguntas=["¿Qué debe verificar el estudiante?"], escenarios=[]))


@pytest.mark.parametrize("cambio", [
    {"historia_id": "../HU-01"},
    {"invest_ok": "true"},
    {"invest_ok": False, "preguntas": ["¿Qué falta?"]},
    {"invest_ok": False, "preguntas": [" "]},
    {"preguntas": ["x" * 501]},
    {"escenarios": []},
    {"escenarios": [dict(ESCENARIO, tipo="otro")]},
    {"escenarios": [dict(ESCENARIO, dado=[])]},
    {"escenarios": [dict(ESCENARIO, cuando=["Una acción"])]},
    {"escenarios": [dict(ESCENARIO, extra=True)]},
    {"extra": True},
])
def test_esquema_rechaza_salidas_invalidas(cambio):
    salida = dict(historia_id="HU-01", invest_ok=True, preguntas=[], escenarios=[ESCENARIO])
    salida.update(cambio)
    assert not Draft7Validator(ESQUEMA).is_valid(salida)


def test_dataset_trazabilidad_y_cobertura():
    casos_por_id = {caso["vars"]["historia_id"]: caso for caso in CASOS}
    assert len(casos_por_id) == len(CASOS) >= 9
    assert casos_por_id["HU-01"]["metadata"]["clasificacion"] == "original"
    for numero, rf in zip(range(2, 7), ("RF-01", "RF-02", "RF-04", "RF-05", "RF-06")):
        metadata = casos_por_id[f"HU-L09-{numero:02d}"]["metadata"]
        assert metadata["clasificacion"] == "provisional"
        assert metadata["requisito"] == rf
        assert metadata["fuente"].startswith("docs/product-backlog-lab09.md#")

    dificiles = [caso for caso in CASOS if caso["metadata"]["clasificacion"] == "no_invest"]
    assert len(dificiles) >= 2 and not any(caso["vars"]["invest_esperado"] for caso in dificiles)
    adversarios = [caso for caso in CASOS if caso["metadata"]["clasificacion"] == "adversario"]
    assert adversarios
    for caso in adversarios:
        assert caso["vars"]["marcador_inyeccion"] in caso["vars"]["historia"]

    for historia_id, caso in casos_por_id.items():
        assert re.fullmatch(r"[A-Z0-9]+(?:-[A-Z0-9]+)*", historia_id)
        assert caso["description"].startswith(historia_id + " ")
        assert caso["vars"]["historia"].strip()
        assert type(caso["vars"]["invest_esperado"]) is bool
        metadata = caso["metadata"]
        assert metadata["necesidad"].strip() and metadata["condiciones_esperadas"]
        fuente, _, referencia = metadata["fuente"].partition("#")
        lineas = (REPO / fuente).read_text(encoding="utf-8").splitlines()
        if re.fullmatch(r"L\d+", referencia):
            assert 1 <= int(referencia[1:]) <= len(lineas)
        else:
            encabezados = {
                re.sub(r"[^\w -]", "", linea[3:].lower()).replace(" ", "-")
                for linea in lineas if linea.startswith("## ")
            }
            assert referencia in encabezados
