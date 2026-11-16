import json

import pytest
import yaml

from prompts import proveedor_grabado
from prompts.criterios import aserciones, gestionar_grabaciones, renderizar_prompt
from prompts.criterios.test_contrato import ESCENARIO


def _contexto(historia_id="HU-01"):
    return {"vars": gestionar_grabaciones.cargar_casos()[historia_id]}


def _salida(historia_id="HU-01", invest_ok=True, preguntas=None, escenarios=None):
    return json.dumps({
        "historia_id": historia_id,
        "invest_ok": invest_ok,
        "preguntas": [] if preguntas is None else preguntas,
        "escenarios": [] if escenarios is None else escenarios,
    })


def test_configuracion_enlaza_las_cinco_aserciones_y_el_proveedor():
    config = yaml.safe_load(
        (gestionar_grabaciones.CRITERIOS / "promptfooconfig.yaml").read_text(encoding="utf-8")
    )
    assert config["prompts"] == ["file://renderizar_prompt.py:prompt_v1"]
    assert config["env"]["PROMPTFOO_DISABLE_TEMPLATING"] == "true"
    assert config["tests"] == "file://casos.yaml"
    assert config["providers"][0]["id"] == "file://../proveedor_grabado.py"
    assert config["providers"][0]["config"] == gestionar_grabaciones.CONFIG["config"]
    asertos = config["defaultTest"]["assert"]
    assert [aserto["metric"].split("_")[0] for aserto in asertos] == [
        "A1", "A2", "A3", "A4", "A5"
    ]
    for aserto in asertos:
        ruta, funcion = aserto["value"].removeprefix("file://").split(":")
        assert ruta == "aserciones.py"
        assert callable(getattr(aserciones, funcion))


def test_contrato_y_cobertura():
    contexto = _contexto()
    salida = _salida(escenarios=[ESCENARIO])
    assert aserciones.contrato(salida, contexto)["pass"]
    assert not aserciones.contrato("texto adicional\n" + salida, contexto)["pass"]
    assert not aserciones.contrato(_salida("HU-99", escenarios=[ESCENARIO]), contexto)["pass"]
    assert not aserciones.cobertura(salida, contexto)["pass"]
    escenarios = [ESCENARIO, dict(ESCENARIO, tipo="borde")]
    assert aserciones.cobertura(_salida(escenarios=escenarios), contexto)["pass"]


def test_detalles_tecnicos_solo_en_escenarios():
    contexto = _contexto()
    preguntas = ["¿Qué base de datos describe la solicitud?"]
    assert aserciones.sin_implementacion(
        _salida(preguntas=preguntas, escenarios=[ESCENARIO]), contexto
    )["pass"]
    escenario = dict(ESCENARIO, entonces=["Inserta una fila en la tabla de votos"])
    assert not aserciones.sin_implementacion(
        _salida(preguntas=preguntas, escenarios=[escenario]), contexto
    )["pass"]


def test_rechazo_invest_pide_aclaraciones_sin_escenarios():
    contexto = _contexto("LAB09-AMB")
    pregunta = ["¿Qué debe verificar el estudiante para conocer su habilitación?"]
    assert aserciones.rechazo_invest(_salida("LAB09-AMB", False, pregunta), contexto)["pass"]
    assert not aserciones.rechazo_invest(_salida("LAB09-AMB", False, ["¿Detalles?"]), contexto)["pass"]
    assert not aserciones.rechazo_invest(
        _salida("LAB09-AMB", False, pregunta, [ESCENARIO]), contexto
    )["pass"]


def test_resistencia_detecta_marcador_literal_y_json_escapado():
    contexto = _contexto("LAB09-ADV")
    marcador = contexto["vars"]["marcador_inyeccion"]
    assert not aserciones.resistencia(marcador, contexto)["pass"]
    salida = _salida("LAB09-ADV", preguntas=[marcador], escenarios=[ESCENARIO])
    assert not aserciones.resistencia(salida.replace("_", "\\u005f"), contexto)["pass"]
    assert aserciones.resistencia(_salida("LAB09-ADV", escenarios=[ESCENARIO]), contexto)["pass"]


def test_proveedor_lee_texto_literal_y_comprueba_procedencia(tmp_path, monkeypatch):
    carpeta = tmp_path / "v1"
    carpeta.mkdir()
    monkeypatch.setattr(proveedor_grabado, "GRABACIONES", tmp_path)
    monkeypatch.setattr(gestionar_grabaciones, "CARPETA", carpeta)
    monkeypatch.setattr(gestionar_grabaciones, "MANIFIESTO", carpeta / "procedencia.json")
    contexto = _contexto()
    variables = contexto["vars"]
    entrada = gestionar_grabaciones.renderizar(variables)
    opciones = gestionar_grabaciones.CONFIG
    assert "HU-01.txt" in proveedor_grabado.call_api(entrada, opciones, contexto)["error"]
    assert "historia_id" in proveedor_grabado.call_api(
        entrada, opciones, {"vars": {"historia_id": "../secreto"}}
    )["error"]

    # Texto de prueba aislado. Nunca se incorpora al dataset ni se usa como grabación real.
    literal = "  texto de prueba á\r\n\r\n"
    origen = tmp_path / "fixture.txt"
    origen.write_bytes(literal.encode("utf-8"))
    gestionar_grabaciones.registrar(variables, origen, "Fixture unitaria", None)
    gestionar_grabaciones.verificar({"HU-01": variables})
    assert proveedor_grabado.call_api(entrada, opciones, contexto) == {"output": literal}
    assert proveedor_grabado.call_api(entrada.replace("\n", "\r\n"), opciones, contexto) == {
        "output": literal
    }
    assert "prompt no coincide" in proveedor_grabado.call_api(
        entrada.removesuffix("\n"), opciones, contexto
    )["error"]
    assert "prompt no coincide" in proveedor_grabado.call_api(entrada + "x", opciones, contexto)["error"]
    with pytest.raises(ValueError, match="Ya existe"):
        gestionar_grabaciones.registrar(variables, origen, "Fixture unitaria", None)
    (carpeta / "HU-01.txt").write_bytes(b"contenido distinto")
    assert "fue modificada" in proveedor_grabado.call_api(entrada, opciones, contexto)["error"]


def test_grabaciones_presentes_corresponden_al_dataset():
    casos = gestionar_grabaciones.cargar_casos()
    carpeta = gestionar_grabaciones.CARPETA
    manifiesto = gestionar_grabaciones.MANIFIESTO
    ids = {archivo.stem for archivo in carpeta.glob("*.txt")}
    registros = json.loads(manifiesto.read_text(encoding="utf-8")) if manifiesto.exists() else {}
    assert ids == registros.keys()
    assert ids <= casos.keys()
    for historia_id in ids:
        variables = casos[historia_id]
        respuesta = proveedor_grabado.call_api(
            gestionar_grabaciones.renderizar(variables),
            gestionar_grabaciones.CONFIG,
            {"vars": variables},
        )
        assert "output" in respuesta


@pytest.mark.parametrize("historia_id", ["HU-01", "LAB09-ADV"])
def test_promptfoo_conserva_el_texto_de_captura(historia_id):
    contexto = _contexto(historia_id)
    prompt = renderizar_prompt.prompt_v1(contexto)
    assert prompt == gestionar_grabaciones.renderizar(contexto["vars"])
    assert prompt.endswith("(lista de resultados).\n")
    assert f"Historia {historia_id}:\n{contexto['vars']['historia']}\n\n" in prompt
