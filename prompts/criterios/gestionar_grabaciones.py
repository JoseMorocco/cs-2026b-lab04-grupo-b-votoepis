"""Renderiza, registra y verifica las entradas y respuestas de v1."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import yaml

from prompts.criterios.renderizar_prompt import renderizar
from prompts.proveedor_grabado import call_api, huella_prompt


CRITERIOS = Path(__file__).resolve().parent
CARPETA = CRITERIOS / "grabaciones" / "v1"
MANIFIESTO = CARPETA / "procedencia.json"
CONFIG = {"config": {"version": "v1"}}


def cargar_casos():
    casos = yaml.safe_load((CRITERIOS / "casos.yaml").read_text(encoding="utf-8"))
    return {caso["vars"]["historia_id"]: caso["vars"] for caso in casos}


def registrar(variables, respuesta, asistente, modelo):
    historia_id = variables["historia_id"]
    destino = CARPETA / f"{historia_id}.txt"
    registros = json.loads(MANIFIESTO.read_text(encoding="utf-8")) if MANIFIESTO.exists() else {}
    if historia_id in registros or destino.exists():
        raise ValueError(f"Ya existe una grabación o procedencia para {historia_id}.")
    contenido = respuesta.read_bytes()
    if not contenido.decode("utf-8").strip() or not asistente.strip():
        raise ValueError("Se requieren una respuesta UTF-8 no vacía y el nombre del asistente.")
    registros[historia_id] = {
        "asistente": asistente,
        "modelo_reportado": modelo,
        "prompt_sha256": huella_prompt(renderizar(variables)),
        "respuesta_sha256": sha256(contenido).hexdigest(),
    }
    with destino.open("xb") as archivo:
        archivo.write(contenido)
    MANIFIESTO.write_text(
        json.dumps(registros, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def verificar(casos):
    errores = []
    if MANIFIESTO.exists():
        registros = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
        extras = registros.keys() - casos.keys()
        errores.extend(f"Procedencia fuera del dataset: {historia_id}" for historia_id in sorted(extras))
    for archivo in sorted(CARPETA.glob("*.txt")):
        if archivo.stem not in casos:
            errores.append(f"Grabación fuera del dataset: {archivo.name}")
    for variables in casos.values():
        respuesta = call_api(renderizar(variables), CONFIG, {"vars": variables})
        if "error" in respuesta:
            errores.append(respuesta["error"])
    if errores:
        raise ValueError("\n".join(errores))
    print(f"{len(casos)} grabaciones verificadas.")


def main():
    casos = cargar_casos()
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest="comando", required=True)
    prompt = comandos.add_parser("prompt")
    prompt.add_argument("id", choices=casos)
    prompt.add_argument("--salida", type=Path)
    registro = comandos.add_parser("registrar")
    registro.add_argument("id", choices=casos)
    registro.add_argument("respuesta", type=Path)
    registro.add_argument("--asistente", required=True)
    registro.add_argument("--modelo")
    comandos.add_parser("verificar")
    args = parser.parse_args()
    try:
        if args.comando == "prompt":
            contenido = renderizar(casos[args.id]).encode("utf-8")
            if args.salida:
                args.salida.write_bytes(contenido)
            else:
                sys.stdout.buffer.write(contenido)
        elif args.comando == "registrar":
            registrar(casos[args.id], args.respuesta, args.asistente, args.modelo)
        else:
            verificar(casos)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
