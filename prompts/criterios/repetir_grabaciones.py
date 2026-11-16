"""Compara 3 replay de v3 en 3 casos; no llama a un modelo ni escribe archivos.

Desde la raíz: python -B -m prompts.criterios.repetir_grabaciones
Imprime JSON con SHA-256 de prompts y respuestas UTF-8 sin normalizar estas
últimas. Un error de procedencia o una diferencia entre replay aborta la ejecución.
"""

from hashlib import sha256
import json

from prompts.criterios.gestionar_grabaciones import cargar_casos
from prompts.criterios.renderizar_iteraciones import prompt_v3
from prompts.proveedor_grabado import call_api, huella_prompt


CASOS = ("HU-01", "LAB09-AMB", "LAB09-ADV")


def main():
    casos = cargar_casos()
    comparacion = []
    for historia_id in CASOS:
        contexto = {"vars": casos[historia_id]}
        prompt = prompt_v3(contexto)
        respuestas = []
        for _ in range(3):
            resultado = call_api(prompt, {"config": {"version": "v3"}}, contexto)
            if "error" in resultado:
                raise RuntimeError(resultado["error"])
            respuestas.append(resultado["output"].encode("utf-8"))
        iguales = respuestas[0] == respuestas[1] == respuestas[2]
        comparacion.append({
            "historia_id": historia_id,
            "prompt_sha256": huella_prompt(prompt),
            "respuestas_sha256": [sha256(respuesta).hexdigest() for respuesta in respuestas],
            "bytes_por_respuesta": [len(respuesta) for respuesta in respuestas],
            "iguales_byte_a_byte": iguales,
        })
        if not iguales:
            raise RuntimeError(f"Replay distinto entre repeticiones de {historia_id}.")
    print(json.dumps({
        "version": "v3",
        "proveedor": "prompts.proveedor_grabado.call_api",
        "limite": "Replay determinista; no verifica no determinismo de un modelo vivo.",
        "comparacion": comparacion,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
