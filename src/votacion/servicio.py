"""Servicio de votación refactorizado con Strategy, Adapter, Factory, Decorator y Observer."""

from src.votacion.decoradores import ConReintentos
from src.votacion.dominio import EstadoEleccion
from src.votacion.elegibilidad import (
    FabricaFuentes,
    PadronLocalAdapter,
    SistemaAcademicoAdapter,
)
from src.votacion.eventos import (
    AuditoriaSeguridad,
    ConfirmacionCorreo,
    PublicadorEventos,
)


class ServicioVotacion:
    def __init__(
        self,
        almacen,
        padron_local,
        sistema_academico,
        correo,
        fabrica=None,
        publicador=None,
    ):
        self.almacen = almacen
        self.padron_local = padron_local
        self.sistema_academico = sistema_academico
        self.correo = correo
        self.fabrica = fabrica or self._crear_fabrica_por_defecto()
        self.publicador = publicador or self._crear_publicador_por_defecto()

    def _crear_fabrica_por_defecto(self) -> FabricaFuentes:
        fabrica = FabricaFuentes()
        fabrica.registrar(
            "LOCAL",
            lambda: ConReintentos(PadronLocalAdapter(self.padron_local)),
        )
        fabrica.registrar(
            "ACADEMICO",
            lambda: ConReintentos(
                SistemaAcademicoAdapter(
                    self.sistema_academico, self.almacen.estudiantes
                )
            ),
        )
        return fabrica

    def _crear_publicador_por_defecto(self) -> PublicadorEventos:
        publicador = PublicadorEventos()
        publicador.suscribir(
            "intento_duplicado",
            AuditoriaSeguridad(self.almacen.eventos_seguridad),
        )
        publicador.suscribir(
            "participacion_registrada",
            ConfirmacionCorreo(self.correo),
        )
        return publicador

    def _solicitud_valida(self, eleccion, estudiante, candidato_id) -> bool:
        if eleccion is None or estudiante is None:
            return False
        if eleccion.estado != EstadoEleccion.ABIERTA:
            return False
        return any(c.id == candidato_id for c in eleccion.candidatos)

    def _registrar_o_auditar(
        self, estudiante_id, eleccion_id, candidato_id
    ) -> bool:
        if self.almacen.existe_participacion(estudiante_id, eleccion_id):
            self.publicador.publicar(
                "intento_duplicado",
                {"estudiante_id": estudiante_id, "eleccion_id": eleccion_id},
            )
            return False

        if not self.almacen.registrar_emision(
            estudiante_id, eleccion_id, candidato_id
        ):
            self.publicador.publicar(
                "intento_duplicado",
                {"estudiante_id": estudiante_id, "eleccion_id": eleccion_id},
            )
            return False
        return True

    def emitir_voto(
        self, estudiante_id, eleccion_id, candidato_id, fuente="LOCAL"
    ) -> bool:
        eleccion = self.almacen.elecciones.get(eleccion_id)
        estudiante = self.almacen.estudiantes.get(estudiante_id)

        if not self._solicitud_valida(eleccion, estudiante, candidato_id):
            return False

        estrategia = self.fabrica.crear(fuente)
        if not estrategia.esta_habilitado(estudiante_id, eleccion_id):
            return False

        if not self._registrar_o_auditar(
            estudiante_id, eleccion_id, candidato_id
        ):
            return False

        self.publicador.publicar(
            "participacion_registrada",
            {
                "eleccion_id": eleccion_id,
                "correo": estudiante.correo_institucional,
            },
        )
        return True