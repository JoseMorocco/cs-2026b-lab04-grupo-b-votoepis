"""Resume una ejecución local de promptfoo 0.125.1."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean

import yaml

from prompts.criterios.renderizar_iteraciones import prompt_v3


CARPETA = Path(__file__).resolve().parent
ESTADOS = {0: "aprobados", 1: "fallidos", 2: "errores"}


def resumir(informe, proveedores, prompts_esperados):
    if len(proveedores) != 2 or not all(p.startswith("ollama:completion:") for p in proveedores):
        raise ValueError("Se esperan dos proveedores locales de Ollama.")
    esperados = {(modelo, caso) for modelo in proveedores for caso in prompts_esperados}
    ejecucion = informe["results"]
    filas = {}
    for fila in ejecucion["results"]:
        modelo, caso = clave = (fila["provider"]["id"], fila["vars"]["historia_id"])
        if clave not in esperados or clave in filas:
            raise ValueError(f"Resultado inesperado o duplicado: {modelo}, {caso}.")
        if fila["prompt"]["raw"] != prompts_esperados[caso]:
            raise ValueError(f"El prompt evaluado difiere de v3: {modelo}, {caso}.")
        estado = ESTADOS.get(fila["failureReason"])
        if estado is None or fila["success"] != (estado == "aprobados"):
            raise ValueError(f"Estado incoherente: {modelo}, {caso}.")
        respuesta = fila.get("response") or {}
        salida = respuesta.get("output")
        latencia = fila.get("latencyMs")
        componentes = (fila.get("gradingResult") or {}).get("componentResults", [])
        filas[clave] = {
            "caso": caso,
            "estado": estado,
            "latencia_ms": latencia,
            "costo_facturado_api_usd": 0,
            "aserciones_fallidas": [
                c["assertion"]["metric"] for c in componentes
                if c.get("assertion") and not c["pass"]
            ],
            "motivo": fila.get("error"),
            "fin": respuesta.get("finishReason"),
            "respuesta_sha256": sha256(salida.encode("utf-8")).hexdigest()
            if isinstance(salida, str) else None,
        }
    if filas.keys() != esperados:
        raise ValueError(f"Faltan resultados: {sorted(esperados - filas.keys())}.")

    totales = Counter(fila["estado"] for fila in filas.values())
    for campo, estado in zip(("successes", "failures", "errors"), ESTADOS.values()):
        if ejecucion["stats"][campo] != totales[estado]:
            raise ValueError(f"El total de {estado} difiere del exportado por promptfoo.")

    modelos = {}
    for modelo in proveedores:
        casos = [filas[modelo, caso] for caso in prompts_esperados]
        conteo = Counter(caso["estado"] for caso in casos)
        latencias = [
            caso["latencia_ms"] for caso in casos
            if caso["estado"] != "errores" and caso["latencia_ms"] is not None
        ]
        modelos[modelo] = {
            "casos": casos,
            **{estado: conteo[estado] for estado in ESTADOS.values()},
            "aprobacion_pct": 100 * conteo["aprobados"] / len(casos),
            "latencia_promedio_ms": mean(latencias) if latencias else None,
            "casos_con_latencia_en_promedio": len(latencias),
            "costo_facturado_api_usd": 0,
        }
    return {
        "eval_id": informe["evalId"],
        "costo_reportado_por_ollama_usd": None,
        "costos_operativos_medidos": False,
        "modelos": modelos,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("informe", type=Path)
    args = parser.parse_args()
    informe = json.loads(args.informe.read_text(encoding="utf-8"))
    config = yaml.safe_load((CARPETA / "promptfooconfig.yaml").read_bytes())
    casos = yaml.safe_load((CARPETA.parent / "criterios" / "casos.yaml").read_bytes())
    proveedores = [p["id"] for p in config["providers"]]
    prompts = {caso["vars"]["historia_id"]: prompt_v3(caso) for caso in casos}
    print(json.dumps(resumir(informe, proveedores, prompts), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
