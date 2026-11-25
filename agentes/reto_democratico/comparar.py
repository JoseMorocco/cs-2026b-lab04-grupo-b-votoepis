"""Compara el crítico de E5 con tres revisores sobre una corrección idéntica."""

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter

from agentes.agente.herramientas import Sandbox
from agentes.agente.politica import ISSUE_CONFIG
from agentes.orquestador import Critico, RevisorSoloLectura
from agentes.reto_democratico.revision import (
    Expediente, RevisorCorreccion, RevisorDiseno, RevisorSeguridad, contar_votos,
)


# Mismo defecto y propuesta que la prueba de la variante B de E5.
DEFECTO = 'def contar(votos):\n    return {"validos": len(votos), "blancos": votos.count(None)}\n'
CORRECCION = '''def contar(votos):
    validos = 0
    blancos = 0
    for voto in votos:
        if voto is None:
            blancos += 1
        else:
            validos += 1
    return {"validos": validos, "blancos": blancos}
'''


def inventario(raiz, rutas):
    return {ruta: sha256((raiz / ruta).read_bytes()).hexdigest() for ruta in sorted(rutas)}


def archivos_controlados(raiz):
    return {
        p.relative_to(raiz).as_posix() for p in raiz.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts
    }


def preparar(origen):
    sandbox = Sandbox(origen, issue="ISSUE-02")
    try:
        (sandbox.raiz / sandbox.editable).write_text(DEFECTO, encoding="utf-8")
        sandbox.original = DEFECTO
        inicial = inventario(sandbox.raiz, sandbox.lecturas)
        sandbox.editar_archivo(sandbox.editable, DEFECTO.strip(), CORRECCION.strip())
        return sandbox, inicial
    except Exception:
        sandbox.cerrar()
        raise


def expediente(sandbox, inicial, pruebas):
    rutas = archivos_controlados(sandbox.raiz)
    actual = inventario(sandbox.raiz, rutas)
    cambiados = tuple(sorted(ruta for ruta in rutas | inicial.keys()
                             if inicial.get(ruta) != actual.get(ruta)))
    return Expediente(
        DEFECTO, sandbox.leer_archivo(sandbox.editable), sandbox.ver_cambios(),
        json.dumps(pruebas, ensure_ascii=False), cambiados, sandbox.editable,
    )


def medir_revision(revisor, datos):
    inicio = perf_counter()
    voto = revisor.revisar(datos)
    return {"duracion_ms": 1000 * (perf_counter() - inicio), "voto": asdict(voto)}, voto


def medir(origen, modalidad):
    sandbox, inicial = preparar(origen)
    try:
        inicio = perf_counter()
        lectura = RevisorSoloLectura(sandbox)
        pruebas = lectura.ejecutar_pruebas()
        datos = expediente(sandbox, inicial, pruebas)
        antes_revision = inventario(sandbox.raiz, archivos_controlados(sandbox.raiz))
        operaciones = ["ejecutar_pruebas", "leer_codigo", "ver_diff", "verificar_integridad"]
        if modalidad == "individual":
            veredicto, motivos = Critico().revisar(datos.diff, pruebas)
            resultado = {"decision": veredicto, "motivos": motivos, "hallazgos": []}
            operaciones.append("critico_e5")
        else:
            revisiones = []
            votos = []
            for revisor in (RevisorCorreccion(), RevisorDiseno(), RevisorSeguridad()):
                medicion, voto = medir_revision(revisor, datos)
                revisiones.append(medicion)
                votos.append(voto)
                operaciones.append("revisar_" + voto.revisor)
            resultado = {**contar_votos(votos), "revisiones": revisiones}
        despues = inventario(sandbox.raiz, archivos_controlados(sandbox.raiz))
        if antes_revision != despues:
            raise RuntimeError("La revisión alteró archivos del sandbox.")
        return {
            "modalidad": modalidad, "duracion_ms": 1000 * (perf_counter() - inicio),
            "operaciones": operaciones, "total_operaciones": len(operaciones),
            "pruebas": pruebas, "diff": datos.diff, "codigo_propuesto": datos.propuesto,
            "archivos_cambiados": datos.archivos_cambiados, "resultado": resultado,
            "revision_sin_escrituras": True,
            "tokens_medidos": None, "costo_monetario_medido": None,
        }
    finally:
        sandbox.cerrar()


def comparar(origen):
    rutas = ISSUE_CONFIG["ISSUE-02"]["lecturas"]
    antes = inventario(origen, rutas)
    individual = medir(origen, "individual")
    democratica = medir(origen, "democratica")
    if individual["diff"] != democratica["diff"]:
        raise RuntimeError("Las modalidades revisaron cambios diferentes.")
    if antes != inventario(origen, rutas):
        raise RuntimeError("Los archivos originales fueron alterados.")
    return {
        "issue": "ISSUE-02", "metodo": "revisores deterministas locales",
        "origen_sha256": antes, "originales_intactos": True,
        "individual": individual, "democratica": democratica,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    if args.salida.exists():
        parser.error("El archivo de evidencia ya existe.")
    resultado = comparar(Path(__file__).resolve().parents[2])
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    with args.salida.open("x", encoding="utf-8", newline="\n") as archivo:
        json.dump(resultado, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")
    print(json.dumps({m: {"decision": resultado[m]["resultado"]["decision"],
                         "duracion_ms": resultado[m]["duracion_ms"]}
                      for m in ("individual", "democratica")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
