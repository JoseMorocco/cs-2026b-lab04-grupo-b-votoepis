"""Diagnóstico de respuestas exportadas por promptfoo, sin alterar el export."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

import yaml

from prompts.criterios import aserciones


CASOS = Path(__file__).resolve().parents[1] / "criterios" / "casos.yaml"
CERCAS = re.compile(r"^ {0,3}(?:`{3,}|~{3,})", re.MULTILINE)
BLOQUES = re.compile(
    r"^ {0,3}(?P<cerca>(?P<marca>`|~)(?P=marca){2,})[^\r\n]*\r?\n"
    r"(?P<contenido>.*?)^ {0,3}(?P=cerca)(?P=marca)*[ \t]*\r?$",
    re.MULTILINE | re.DOTALL,
)
ID_LITERAL = re.compile(
    r'"historia_id"\s*:\s*("(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*")'
)


def _constante_invalida(valor):
    raise ValueError(f"Constante no válida en JSON: {valor}")


def analizar_json(texto, variables, marcadores):
    try:
        datos = json.loads(texto, parse_constant=_constante_invalida)
    except ValueError as error:
        return {"json_valido": False, "error_json": str(error)}

    es_objeto = isinstance(datos, dict)
    historia_id = datos.get("historia_id") if es_objeto else None
    errores = [
        {"ruta": error.json_path, "regla": error.validator, "motivo": error.message}
        for error in aserciones.VALIDADOR.iter_errors(datos)
    ]
    # Evaluación hipotética del contenido para localizar problemas adicionales.
    adicionales = {}
    if es_objeto:
        for etiqueta, revisar in (
            ("A2", aserciones.cobertura), ("A3", aserciones.sin_implementacion),
            ("A4", aserciones.rechazo_invest), ("A5", aserciones.resistencia),
        ):
            resultado = revisar(texto, {"vars": variables})
            if not resultado["pass"]:
                adicionales[etiqueta] = resultado["reason"]
    texto_decodificado = json.dumps(datos, ensure_ascii=False)
    return {
        "json_valido": True,
        "esquema_valido": not errores,
        "errores_esquema": errores,
        "historia_id": historia_id,
        "id_coincide": historia_id == variables["historia_id"],
        "marcadores_decodificados": [m for m in marcadores if m in texto_decodificado],
        "fallos_adicionales": adicionales,
    }


def auditar_respuesta(texto, variables, marcadores):
    if not isinstance(texto, str):
        return {"respuesta_presente": False}
    return {
        "respuesta_presente": True,
        "respuesta_sha256": sha256(texto.encode("utf-8")).hexdigest(),
        "tiene_cercas_markdown": bool(CERCAS.search(texto)),
        "marcadores_literales": [marcador for marcador in marcadores if marcador in texto],
        "ids_textuales": [json.loads(id_) for id_ in ID_LITERAL.findall(texto)],
        "respuesta_literal": analizar_json(texto, variables, marcadores),
        "bloques": [
            analizar_json(bloque["contenido"], variables, marcadores)
            for bloque in BLOQUES.finditer(texto)
        ],
    }


def auditar(archivo):
    original = archivo.read_bytes()
    informe = json.loads(original)
    variables = {c["vars"]["historia_id"]: c["vars"] for c in yaml.safe_load(CASOS.read_bytes())}
    marcadores = sorted({v["marcador_inyeccion"] for v in variables.values()
                          if "marcador_inyeccion" in v})
    analisis = []
    for registro in informe["results"]["results"]:
        caso = registro["vars"]["historia_id"]
        analisis.append({
            "modelo": registro["provider"]["id"],
            "caso": caso,
            "estado_original": registro["failureReason"],
            **auditar_respuesta((registro.get("response") or {}).get("output"),
                                variables[caso], marcadores),
        })
    return {
        "eval_id": informe["evalId"],
        "informe_sha256": sha256(original).hexdigest(),
        "analisis": analisis,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("informe", type=Path)
    args = parser.parse_args()
    print(json.dumps(auditar(args.informe), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
