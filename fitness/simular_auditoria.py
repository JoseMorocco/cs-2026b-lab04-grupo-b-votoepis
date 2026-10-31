"""E4 / S4: paquete de auditoría comprobable, con conjunto sintético.

La copia de la huella en el 'canal externo' se simula mediante un valor que el
auditado no puede editar. NO equivale a publicarla realmente fuera de la BD.
"""
import hashlib
import json
from pathlib import Path

EVIDENCIA = (Path(__file__).resolve().parents[1] /
            "docs/architecture/add/evidencias/auditoria.json")


def generar_votos(cantidad: int = 25_000) -> list[dict]:
    if cantidad <= 0:
        raise ValueError("cantidad debe ser positiva")
    # IDs de orden de exportación, NO identidades de estudiantes.
    return [{"eleccion_id": 1, "candidato_id": 1 + i % 3}
            for i in range(cantidad)]


def canonico(votos: list[dict]) -> bytes:
    # Contrato del export: lista ordenada, UTF-8, JSON compacto y claves ordenadas.
    return json.dumps(votos, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def resumen(votos: list[dict]) -> dict:
    totales = {}
    for voto in votos:
        candidato = str(voto["candidato_id"])
        totales[candidato] = totales.get(candidato, 0) + 1
    return dict(sorted(totales.items()))


def preparar_paquete(votos: list[dict]) -> tuple[dict, str]:
    """Acta, listado y copia externa de la huella (simulada)."""
    listado = [dict(v) for v in votos]
    huella = hashlib.sha256(canonico(listado)).hexdigest()
    paquete = {"acta": {"eleccion_id": 1, "total_votos": len(listado),
                         "totales": resumen(listado), "sha256": huella},
               "listado": listado}
    return paquete, huella  # copia fuera del paquete: testigo del auditor


def verificar(paquete: dict, huella_externa: str) -> bool:
    try:
        listado, acta = paquete["listado"], paquete["acta"]
        if any(set(v) != {"eleccion_id", "candidato_id"} or
               v["eleccion_id"] != acta["eleccion_id"] for v in listado):
            return False
        digest = hashlib.sha256(canonico(listado)).hexdigest()
        return (digest == huella_externa == acta["sha256"]
                and len(listado) == acta["total_votos"]
                and resumen(listado) == acta["totales"])
    except (KeyError, TypeError, ValueError):
        return False


def comparar(cantidad: int = 25_000) -> dict:
    votos = generar_votos(cantidad)
    # Modelo base: publicar solamente los totales, sin paquete verificable.
    solo_totales = {"totales": resumen(votos)}
    paquete, externa = preparar_paquete(votos)
    valido = verificar(paquete, externa)
    alterado = {"acta": dict(paquete["acta"]),
               "listado": [dict(v) for v in paquete["listado"]]}
    alterado["listado"][0]["candidato_id"] = 2
    deteccion_alteracion = not verificar(alterado, externa)
    acta_alterada = {"acta": dict(paquete["acta"]), "listado": paquete["listado"]}
    acta_alterada["acta"]["totales"] = dict(paquete["acta"]["totales"])
    acta_alterada["acta"]["totales"]["1"] += 1
    deteccion_totales = not verificar(acta_alterada, externa)
    return {
        "escenario": "S4", "votos_sinteticos": cantidad,
        "antes": {"resultados_publicados": len(solo_totales),
                  "resultados_con_acta_y_listado_verificable": 0,
                  "porcentaje_resultados_verificables": 0},
        "despues": {"resultados_publicados": 1,
                    "resultados_con_acta_y_listado_verificable": int(valido),
                    "porcentaje_resultados_verificables": 100 if valido else 0,
                    "diferencias_conteo": 0 if valido else 1,
                    "alteracion_de_voto_detectada": deteccion_alteracion,
                    "alteracion_de_totales_detectada": deteccion_totales,
                    "votos_con_campo_estudiante": sum("estudiante_id" in v for v in votos),
                    "cumple_s4_en_prototipo": valido and deteccion_alteracion and deteccion_totales},
        "limite": "La huella externa es una copia mantenida por el test; no se publica realmente.",
    }


def main():
    resultado = comparar()
    EVIDENCIA.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCIA.write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    if not resultado["despues"]["cumple_s4_en_prototipo"]:
        raise SystemExit("Resultado inesperado de S4")


if __name__ == "__main__":
    main()
