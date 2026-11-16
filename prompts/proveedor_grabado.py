"""Proveedor local de promptfoo para reproducir respuestas registradas."""

from hashlib import sha256
import json
from pathlib import Path
import re


GRABACIONES = Path(__file__).resolve().parent / "criterios" / "grabaciones"


def huella_prompt(prompt):
    return sha256(prompt.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def call_api(prompt, options, context):
    version = options.get("config", {}).get("version")
    historia_id = context.get("vars", {}).get("historia_id")
    if not isinstance(version, str) or not re.fullmatch(r"v[1-9]\d*", version):
        return {"error": "Configura una versión de grabaciones con formato v1, v2, etc."}
    if not isinstance(historia_id, str) or not re.fullmatch(
        r"[A-Z0-9]+(?:-[A-Z0-9]+)*", historia_id
    ):
        return {"error": "Falta un historia_id válido en las variables del caso."}

    carpeta = GRABACIONES / version
    try:
        respuesta = (carpeta / f"{historia_id}.txt").read_bytes()
    except OSError as error:
        return {"error": f"No se pudo leer la grabación {version}/{historia_id}.txt: {error.strerror}"}

    try:
        registros = json.loads((carpeta / "procedencia.json").read_text(encoding="utf-8"))
        registro = registros[historia_id]
        if not registro["asistente"].strip():
            raise ValueError("asistente vacío")
        if registro["prompt_sha256"] != huella_prompt(prompt):
            return {"error": f"El prompt no coincide con la procedencia de {version}/{historia_id}."}
        if registro["respuesta_sha256"] != sha256(respuesta).hexdigest():
            return {"error": f"La respuesta grabada fue modificada: {version}/{historia_id}."}
        return {"output": respuesta.decode("utf-8")}
    except (OSError, KeyError, ValueError, TypeError, AttributeError):
        return {"error": f"Procedencia ausente o inválida para {version}/{historia_id}."}
