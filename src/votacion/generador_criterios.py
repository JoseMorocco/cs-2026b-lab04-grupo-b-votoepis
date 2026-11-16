"""Generación de criterios mediante el puerto LLM y los contratos de Lab 09.

No modifica las plantillas ni repara respuestas: exige un objeto JSON conforme
al esquema y al identificador solicitado. La procedencia y la reproducción de
los bytes originales quedan a cargo del proveedor inyectado.
"""

import json

from prompts.criterios.aserciones import contrato
from prompts.criterios.renderizar_iteraciones import prompt_v2, prompt_v3
from prompts.criterios.renderizar_prompt import prompt_v1

from .ia import ProveedorLLM


class GeneradorCriterios:
    """Carga v1, v2 o v3 con su renderizador original y valida la salida.

    ``generar(historia_id, historia)`` devuelve el objeto JSON validado o lanza
    ``ValueError`` con el motivo del contrato. Los errores del proveedor se
    propagan sin reintentos ni respuestas alternativas.
    """

    def __init__(self, proveedor: ProveedorLLM, version: str = "v1"):
        renderizadores = {"v1": prompt_v1, "v2": prompt_v2, "v3": prompt_v3}
        if version not in renderizadores:
            raise ValueError(f"Versión de criterios no soportada: {version}")
        self.proveedor = proveedor
        self._renderizar = renderizadores[version]

    def generar(self, historia_id: str, historia: str) -> dict:
        contexto = {"vars": {"historia_id": historia_id, "historia": historia}}
        respuesta = self.proveedor.completar(self._renderizar(contexto))
        resultado = contrato(respuesta, contexto)
        if not resultado["pass"]:
            raise ValueError(resultado["reason"])
        return json.loads(respuesta)
