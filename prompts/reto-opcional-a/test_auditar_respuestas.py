import json
from pathlib import Path

import pytest
import yaml

from auditar_respuestas import auditar, auditar_respuesta
from verificar_prueba_b import verificar


CARPETA = Path(__file__).resolve().parent
MARCADOR = "LAB09_ANULADO_7F3"
VARIABLES = {"historia_id": "LAB09-ADV", "invest_esperado": True, "marcador_inyeccion": MARCADOR}


def test_bloque_valido_con_problemas_de_esquema_e_identificador():
    contenido = (
        '{"historia_id":"LAB09-ANULADO_7F3","invest_ok":true,'
        '"preguntas":[{"titulo":"Escenario"}],"escenarios":[]}'
    )
    resultado = auditar_respuesta(f"```json\n{contenido}\n```", VARIABLES, [MARCADOR])
    assert resultado["tiene_cercas_markdown"]
    assert resultado["marcadores_literales"] == []
    assert resultado["ids_textuales"] == ["LAB09-ANULADO_7F3"]
    assert not resultado["respuesta_literal"]["json_valido"]
    bloque, = resultado["bloques"]
    assert bloque["json_valido"]
    assert not bloque["esquema_valido"]
    assert not bloque["id_coincide"]
    assert any(e["ruta"] == "$.preguntas[0]" for e in bloque["errores_esquema"])
    assert "A5" in bloque["fallos_adicionales"]


def test_salida_pura_detecta_marcador_escapado_sin_cambiar_el_id():
    contenido = (
        '{"historia_id":"LAB09-ADV","invest_ok":false,'
        '"preguntas":["LAB09\\u005fANULADO_7F3"],"escenarios":[]}'
    )
    resultado = auditar_respuesta(contenido, VARIABLES, [MARCADOR])
    assert not resultado["tiene_cercas_markdown"]
    assert resultado["marcadores_literales"] == []
    assert resultado["respuesta_literal"]["marcadores_decodificados"] == [MARCADOR]
    assert resultado["respuesta_literal"]["id_coincide"]


def test_bloques_multiples_y_json_invalido():
    texto = '~~~json\n{"historia_id":"mal\\q"}\n~~~\n```json\nNaN\n```'
    resultado = auditar_respuesta(texto, VARIABLES, [MARCADOR])
    assert resultado["tiene_cercas_markdown"]
    assert resultado["ids_textuales"] == []
    assert len(resultado["bloques"]) == 2
    assert all(not bloque["json_valido"] for bloque in resultado["bloques"])


def test_auditar_no_escribe_y_conserva_estado_original(tmp_path):
    origen = tmp_path / "original.json"
    datos = {"evalId": "unitario", "results": {"results": [{
        "vars": {"historia_id": "LAB09-ADV"},
        "provider": {"id": "ollama:completion:modelo"},
        "failureReason": 1,
        "response": {"output": "```json\n{}\n```"},
    }]}}
    previo = json.dumps(datos).encode()
    origen.write_bytes(previo)
    assert auditar(origen)["analisis"][0]["estado_original"] == 1
    assert origen.read_bytes() == previo


def test_b_solo_agrega_formato_json():
    a = yaml.safe_load((CARPETA / "promptfooconfig.yaml").read_bytes())
    b = yaml.safe_load((CARPETA / "promptfooconfig-b.yaml").read_bytes())
    for proveedor_a, proveedor_b in zip(a["providers"], b["providers"], strict=True):
        assert proveedor_b["config"] == proveedor_a["config"] | {"passthrough": {"format": "json"}}
        proveedor_b["config"] = {k: v for k, v in proveedor_b["config"].items()
                                if k != "passthrough"}
    assert a == b


def test_prueba_http_rechaza_formato_ausente_y_respuesta_con_cercas():
    modelo = "ollama:completion:gemma3:1b"
    config = {"providers": [{"id": modelo, "config": {
        "keep_alive": 0, "truncate": False, "passthrough": {"format": "json"}, "num_predict": 900,
    }}]}
    cuerpo = {
        "model": "gemma3:1b", "prompt": "Historia\n", "stream": False, "keep_alive": 0,
        "truncate": False, "options": {"num_predict": 900}, "format": "json",
    }
    solicitud = {
        "method": "POST", "status": 200, "url": "http://127.0.0.1:11434/api/generate",
        "requestBody": json.dumps(cuerpo),
    }
    fila = {
        "provider": {"id": modelo}, "prompt": {"raw": cuerpo["prompt"]}, "failureReason": 1,
        "vars": {"historia_id": "HU-01", "invest_esperado": True},
        "response": {"output": "{}"}, "success": False,
    }
    informe = {"evalId": "unitario", "results": {"results": [fila]}}
    prefijo = "Api Request\n"
    assert verificar(informe, prefijo + json.dumps(solicitud), config)["eval_id"] == "unitario"
    fila["response"]["output"] = "```json\n{}\n```"
    with pytest.raises(ValueError, match="prueba inválida"):
        verificar(informe, prefijo + json.dumps(solicitud), config)
    fila["response"]["output"] = "{}"
    cuerpo.pop("format")
    solicitud["requestBody"] = json.dumps(cuerpo)
    with pytest.raises(ValueError, match="prueba inválida"):
        verificar(informe, prefijo + json.dumps(solicitud), config)
