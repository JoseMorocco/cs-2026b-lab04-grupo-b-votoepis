

from abc import ABC

from src.votacion.dominio import EstadoEleccion


class EstadoBase(ABC):
    nombre = None

    def abrir(self, eleccion, padron_cargado=False):
        raise ValueError("No se puede abrir desde este estado")

    def cerrar(self, eleccion):
        raise ValueError("No se puede cerrar desde este estado")

    def iniciar_escrutinio(self, eleccion, autorizado=False):
        raise ValueError("No se puede escrutar desde este estado")

    def publicar_resultados(
        self, eleccion, acta_firmada=False, totales_verificados=False
    ):
        raise ValueError("No se pueden publicar resultados desde este estado")


class Configurada(EstadoBase):
    nombre = EstadoEleccion.CONFIGURADA

    def abrir(self, eleccion, padron_cargado=False):
        if not padron_cargado or not eleccion.candidatos:
            raise ValueError("Faltan padrón o candidatos")
        eleccion.estado = EstadoEleccion.ABIERTA


class Abierta(EstadoBase):
    nombre = EstadoEleccion.ABIERTA

    def cerrar(self, eleccion):
        eleccion.estado = EstadoEleccion.CERRADA


class Cerrada(EstadoBase):
    nombre = EstadoEleccion.CERRADA

    def iniciar_escrutinio(self, eleccion, autorizado=False):
        if not autorizado:
            raise ValueError("Comité no autorizado")
        eleccion.estado = EstadoEleccion.ESCRUTADA


class Escrutada(EstadoBase):
    nombre = EstadoEleccion.ESCRUTADA

    def publicar_resultados(
        self, eleccion, acta_firmada=False, totales_verificados=False
    ):
        if not acta_firmada or not totales_verificados:
            raise ValueError("Acta o totales no verificados")
        eleccion.estado = EstadoEleccion.PUBLICADA


class Publicada(EstadoBase):
    nombre = EstadoEleccion.PUBLICADA


ESTADOS = {
    EstadoEleccion.CONFIGURADA: Configurada(),
    EstadoEleccion.ABIERTA: Abierta(),
    EstadoEleccion.CERRADA: Cerrada(),
    EstadoEleccion.ESCRUTADA: Escrutada(),
    EstadoEleccion.PUBLICADA: Publicada(),
}
