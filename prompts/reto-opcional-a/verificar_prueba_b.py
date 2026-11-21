"""Comprueba en la traza HTTP que la prueba corta activó el modo JSON."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

import yaml

from auditar_respuestas import auditar_respuesta


def verificar(informe, traza, config):
    modelos = {p["id"].removeprefix("ollama:completion:"): p["config"]
               for p in config["providers"]}
    filas = informe["results"]["results"]
    por_modelo = {fila["provider"]["id"].removeprefix("ollama:completion:"): fila
                  for fila in filas}
    if len(filas) != len(modelos) or por_modelo.keys() != modelos.keys():
        raise ValueError("Se necesita una respuesta de prueba por modelo.")

    comprobadas = {}
    decodificar = json.JSONDecoder().raw_decode
    for entrada in re.finditer(r"Api Request\n(?=\{)", traza):
        llamada, _ = decodificar(traza[entrada.end():])
        if llamada.get("url") != "http://127.0.0.1:11434/api/generate":
            continue
        cuerpo = json.loads(llamada["requestBody"])
        modelo = cuerpo["model"]
        if modelo not in modelos or modelo in comprobadas:
            raise ValueError(f"Solicitud inesperada o duplicada: {modelo}.")
        configurado = modelos[modelo]
        fila = por_modelo[modelo]
        salida = fila["response"]["output"]
        auditoria = auditar_respuesta(salida, fila["vars"], [])
        esperados = {
            "model": modelo,
            "prompt": fila["prompt"]["raw"],
            "stream": False,
            "options": {k: v for k, v in configurado.items()
                        if k not in ("keep_alive", "truncate", "passthrough")},
            "keep_alive": configurado["keep_alive"],
            "truncate": configurado["truncate"],
            "format": "json",
        }
        if (llamada["method"] != "POST" or llamada["status"] != 200
                or cuerpo != esperados or fila["vars"]["historia_id"] != "HU-01"
                or fila["failureReason"] == 2
                or not auditoria["respuesta_literal"]["json_valido"]):
            raise ValueError(f"Solicitud HTTP o respuesta JSON de prueba inválida: {modelo}.")
        evidencia = {k: v for k, v in cuerpo.items() if k != "prompt"}
        comprobadas[modelo] = {
            "url": llamada["url"],
            "estado_http": llamada["status"],
            "solicitud": evidencia,
            "prompt_sha256": sha256(cuerpo["prompt"].encode("utf-8")).hexdigest(),
            "respuesta_sha256": auditoria["respuesta_sha256"],
            "aprobado_promptfoo": fila["success"],
        }
    if comprobadas.keys() != modelos.keys():
        raise ValueError("Falta evidencia HTTP de uno o más modelos.")
    return {"eval_id": informe["evalId"], "solicitudes": comprobadas}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directorio", type=Path)
    carpeta = parser.parse_args().directorio
    informe = json.loads((carpeta / "prueba.json").read_bytes())
    traza = (carpeta / "prueba-debug.log").read_text(encoding="utf-8")
    config = yaml.safe_load((carpeta / "configuracion.yaml").read_bytes())
    print(json.dumps(verificar(informe, traza, config), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
