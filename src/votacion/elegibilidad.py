"""Strategy, Adapter y Factory para la habilitación electoral."""

from collections.abc import Callable

from src.votacion.dominio import PadronPort


class PadronLocalAdapter(PadronPort):
    """Adapter del padrón local simulado."""

    def __init__(self, proveedor):
        self._proveedor = proveedor

    def esta_habilitado(self, estudiante_id, eleccion_id):
        return self._proveedor.esta_habilitado(
            estudiante_id, eleccion_id
        )


class SistemaAcademicoAdapter(PadronPort):
    """Adapter de la interfaz del sistema académico simulado."""

    def __init__(self, proveedor, estudiantes):
        self._proveedor = proveedor
        self._estudiantes = estudiantes

    def esta_habilitado(self, estudiante_id, eleccion_id):
        codigo = self._estudiantes[estudiante_id].codigo
        respuesta = self._proveedor.consultar_condicion(
            codigo, eleccion_id
        )
        return respuesta["situacion"] == "HABILITADO"


class FabricaFuentes:
    """Factory basada en registro de estrategias."""

    def __init__(self):
        self._creadores: dict[str, Callable[[], PadronPort]] = {}

    def registrar(self, nombre, creador):
        self._creadores[nombre] = creador

    def crear(self, nombre):
        if nombre not in self._creadores:
            raise ValueError(
                f"Fuente de habilitación no soportada: {nombre}"
            )

        return self._creadores[nombre]()
