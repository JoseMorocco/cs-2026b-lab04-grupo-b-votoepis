"""Asistente del reglamento VotoEPIS; aislado del proceso de votación."""
from abc import ABC, abstractmethod
import re


class ProveedorLLM(ABC):
    @abstractmethod
    def completar(self, prompt: str) -> str:
        ...


class AdaptadorLLMSimulado(ProveedorLLM):
    """Adapter de un cliente simulado con interfaz responder(texto)."""
    def __init__(self, cliente):
        self.cliente = cliente

    def completar(self, prompt: str) -> str:
        return self.cliente.responder(prompt)


class ConCache(ProveedorLLM):
    def __init__(self, interno: ProveedorLLM):
        self.interno = interno
        self.cache = {}

    def completar(self, prompt: str) -> str:
        if prompt not in self.cache:
            self.cache[prompt] = self.interno.completar(prompt)
        return self.cache[prompt]


class Guardrail(ABC):
    def __init__(self, siguiente=None):
        self.siguiente = siguiente

    def validar(self, respuesta: str) -> str:
        respuesta = self._validar(respuesta)
        return self.siguiente.validar(respuesta) if self.siguiente else respuesta

    @abstractmethod
    def _validar(self, respuesta: str) -> str:
        ...


class SinIndicacionesDeVoto(Guardrail):
    def _validar(self, respuesta: str) -> str:
        if re.search(r"\b(vota|voten|elige|apoya)\s+(por|a)\b", respuesta, re.I):
            raise ValueError("Guardrail: recomendación de voto")
        return respuesta


class SinResultadosInventados(Guardrail):
    def _validar(self, respuesta: str) -> str:
        if re.search(r"\b(gan[oó]|ganador(?:a)?|resultados? oficiales?)\b", respuesta, re.I):
            raise ValueError("Guardrail: afirmación sobre resultados electorales")
        return respuesta


class AsistenteReglamento:
    def __init__(self, proveedor: ProveedorLLM, guardrails: Guardrail, contexto: str):
        self.proveedor = proveedor
        self.guardrails = guardrails
        self.contexto = contexto

    def responder(self, pregunta: str) -> str:
        if not pregunta.strip():
            raise ValueError("La pregunta no puede estar vacía")
        prompt = (
            "Responde exclusivamente usando el reglamento adjunto. "
            "Si no hay evidencia, indica que no está especificado. "
            "No recomiendes candidaturas ni inventes resultados.\n"
            f"Reglamento:\n{self.contexto}\nPregunta: {pregunta}"
        )
        return self.guardrails.validar(self.proveedor.completar(prompt))


class ClienteLLMFalso:
    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.llamadas = 0

    def responder(self, prompt):
        self.llamadas += 1
        return self.respuesta
