"""Decorator para reintentos de consultas al padrón."""
from src.votacion.dominio import PadronPort


class ConReintentos(PadronPort):
    def __init__(self, interno: PadronPort, intentos: int = 3):
        if intentos < 1:
            raise ValueError("El número de intentos debe ser positivo")
        self.interno = interno
        self.intentos = intentos

    def esta_habilitado(self, estudiante_id, eleccion_id) -> bool:
        for intento in range(self.intentos):
            try:
                return self.interno.esta_habilitado(estudiante_id, eleccion_id)
            except TimeoutError:
                if intento == self.intentos - 1:
                    return False
        return False
