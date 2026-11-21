from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest
import yaml

from metricas import resumir


CARPETA = Path(__file__).resolve().parent
MODELOS = ("ollama:completion:gemma3:1b", "ollama:completion:qwen2.5:1.5b-instruct-q4_K_M")
PROMPTS = {"HU-01": "Entradilla\n", "LAB09-AMB": "Historia ambigua\n"}


@pytest.fixture
def informe():
    """Ejemplo unitario de la estructura del export, separado de toda medición."""
    filas = []
    for modelo, estados in zip(MODELOS, ((0, 1), (0, 2))):
        for (caso, prompt), estado in zip(PROMPTS.items(), estados):
            filas.append({
                "provider": {"id": modelo},
                "vars": {"historia_id": caso},
                "prompt": {"raw": prompt},
                "failureReason": estado,
                "success": estado == 0,
                "latencyMs": [150, 250, 800][estado],
                "response": {"output": " ejemplo literal\n"} if estado != 2 else {"error": "timeout"},
                "gradingResult": {
                    "componentResults": [{"pass": False, "assertion": {"metric": "A1_contrato"}}]
                } if estado == 1 else None,
            })
    return {"evalId": "prueba-unitaria", "results": {
        "results": filas, "stats": {"successes": 2, "failures": 1, "errors": 1},
    }}


def test_agrupa_mediciones_y_distingue_error_de_fallo(informe):
    resumen = resumir(informe, MODELOS, PROMPTS)
    gemma, qwen = (resumen["modelos"][modelo] for modelo in MODELOS)
    assert (gemma["aprobados"], gemma["fallidos"], gemma["errores"]) == (1, 1, 0)
    assert gemma["aprobacion_pct"] == 50
    assert gemma["latencia_promedio_ms"] == 200
    assert gemma["casos"][1]["aserciones_fallidas"] == ["A1_contrato"]
    assert gemma["casos"][0]["respuesta_sha256"] == sha256(b" ejemplo literal\n").hexdigest()
    assert (qwen["aprobados"], qwen["fallidos"], qwen["errores"]) == (1, 0, 1)
    assert qwen["latencia_promedio_ms"] == 150
    assert qwen["casos"][1]["latencia_ms"] == 800
    assert qwen["costo_facturado_api_usd"] == 0
    assert resumen["costo_reportado_por_ollama_usd"] is None
    assert not resumen["costos_operativos_medidos"]


def test_detecta_falta_duplicado_y_prompt_distinto(informe):
    filas = informe["results"]["results"]
    ultima = filas.pop()
    with pytest.raises(ValueError, match="Faltan resultados"):
        resumir(informe, MODELOS, PROMPTS)
    filas.extend([ultima, deepcopy(ultima)])
    with pytest.raises(ValueError, match="duplicado"):
        resumir(informe, MODELOS, PROMPTS)
    filas.pop()
    filas[0]["prompt"]["raw"] = PROMPTS["HU-01"].rstrip("\n")
    with pytest.raises(ValueError, match="difiere de v3"):
        resumir(informe, MODELOS, PROMPTS)


def test_usamos_el_mismo_v3_dataset_y_aserciones():
    actual = yaml.safe_load((CARPETA / "promptfooconfig.yaml").read_bytes())
    referencia = yaml.safe_load(
        (CARPETA.parent / "criterios" / "promptfooconfig-v3.yaml").read_bytes()
    )
    assert actual["prompts"] == ["file://../criterios/renderizar_iteraciones.py:prompt_v3"]
    assert actual["tests"] == "file://../criterios/casos.yaml"
    assert actual["env"]["PROMPTFOO_DISABLE_TEMPLATING"] == "true"
    for aserto in actual["defaultTest"]["assert"]:
        aserto["value"] = aserto["value"].replace("file://../criterios/", "file://")
    assert actual["defaultTest"] == referencia["defaultTest"]
    assert [p["id"] for p in actual["providers"]] == list(MODELOS)
    assert actual["providers"][0]["config"] == actual["providers"][1]["config"]
    assert actual["commandLineOptions"]["maxConcurrency"] == 1
