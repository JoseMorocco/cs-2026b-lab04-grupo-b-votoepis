"""Servicio de votación: Strategy, Adapter, Factory, Observer, Decorator."""
from src.votacion.dominio import EstadoEleccion
from src.votacion.decoradores import ConReintentos
from src.votacion.elegibilidad import (
    FabricaFuentes, PadronLocalAdapter, SistemaAcademicoAdapter,
)
from src.votacion.eventos import (
    PublicadorEventos, ConfirmacionCorreo, AuditoriaSeguridad,
)


class ServicioVotacion:
    def __init__(
        self, almacen, padron_local, sistema_academico, correo,
        fabrica=None, publicador=None,
    ):
        self.almacen = almacen
        self.correo = correo

        if fabrica is None:
            fabrica = FabricaFuentes()
            fabrica.registrar("LOCAL", lambda: PadronLocalAdapter(padron_local))
            fabrica.registrar(
                "ACADEMICO",
                lambda: SistemaAcademicoAdapter(
                    sistema_academico, almacen.estudiantes
                ),
            )
        self.fabrica = fabrica

        self.publicador = publicador or PublicadorEventos()
        self.publicador.suscribir(
            "participacion_registrada", ConfirmacionCorreo(correo)
        )
        self.publicador.suscribir(
            "intento_duplicado", AuditoriaSeguridad(almacen.eventos_seguridad)
        )

    def emitir_voto(self, estudiante_id, eleccion_id, candidato_id, fuente="LOCAL"):
        eleccion = self.almacen.elecciones.get(eleccion_id)
        if eleccion is None or eleccion.estado != EstadoEleccion.ABIERTA:
            return False

        estudiante = self.almacen.estudiantes.get(estudiante_id)
        if estudiante is None:
            return False

        if candidato_id not in [c.id for c in eleccion.candidatos]:
            return False

        estrategia = ConReintentos(self.fabrica.crear(fuente), intentos=3)
        if not estrategia.esta_habilitado(estudiante_id, eleccion_id):
            return False

        datos_auditoria = {
            "estudiante_id": estudiante_id,
            "eleccion_id": eleccion_id,
        }
        if self.almacen.existe_participacion(estudiante_id, eleccion_id):
            self.publicador.publicar("intento_duplicado", datos_auditoria)
            return False

        guardado = self.almacen.registrar_emision(
            estudiante_id, eleccion_id, candidato_id
        )
        if not guardado:
            self.publicador.publicar("intento_duplicado", datos_auditoria)
            return False

        self.publicador.publicar("participacion_registrada", {
            "correo": estudiante.correo_institucional,
            "eleccion_id": eleccion_id,
        })
        return True
