"""Servicio de votación refactorizado con Strategy, Adapter y Factory."""

from src.votacion.dominio import EstadoEleccion
from src.votacion.elegibilidad import (
    FabricaFuentes,
    PadronLocalAdapter,
    SistemaAcademicoAdapter,
)


class ServicioVotacion:
    def __init__(
        self,
        almacen,
        padron_local,
        sistema_academico,
        correo,
        fabrica=None,
    ):
        self.almacen = almacen
        self.correo = correo

        if fabrica is None:
            fabrica = FabricaFuentes()
            fabrica.registrar(
                "LOCAL",
                lambda: PadronLocalAdapter(padron_local),
            )
            fabrica.registrar(
                "ACADEMICO",
                lambda: SistemaAcademicoAdapter(
                    sistema_academico,
                    almacen.estudiantes,
                ),
            )

        self.fabrica = fabrica

    def emitir_voto(
        self, estudiante_id, eleccion_id, candidato_id, fuente="LOCAL"
    ):
        eleccion = self.almacen.elecciones.get(eleccion_id)

        if eleccion is None:
            return False

        if eleccion.estado != EstadoEleccion.ABIERTA:
            return False

        estudiante = self.almacen.estudiantes.get(estudiante_id)

        if estudiante is None:
            return False

        if candidato_id not in [c.id for c in eleccion.candidatos]:
            return False

        estrategia = self.fabrica.crear(fuente)

        habilitado = False

        for intento in range(3):
            try:
                habilitado = estrategia.esta_habilitado(
                    estudiante_id, eleccion_id
                )
                break
            except TimeoutError:
                if intento == 2:
                    return False

        if not habilitado:
            return False

        if self.almacen.existe_participacion(
            estudiante_id, eleccion_id
        ):
            self.almacen.eventos_seguridad.append({
                "tipo": "INTENTO_DUPLICADO",
                "estudiante_id": estudiante_id,
                "eleccion_id": eleccion_id,
            })
            return False

        guardado = self.almacen.registrar_emision(
            estudiante_id, eleccion_id, candidato_id
        )

        if not guardado:
            self.almacen.eventos_seguridad.append({
                "tipo": "INTENTO_DUPLICADO",
                "estudiante_id": estudiante_id,
                "eleccion_id": eleccion_id,
            })
            return False

        if estudiante.correo_institucional:
            self.correo.enviar(
                estudiante.correo_institucional,
                "Confirmación de participación en VotoEPIS",
                "Tu participación en la elección fue registrada.",
            )

        return True
