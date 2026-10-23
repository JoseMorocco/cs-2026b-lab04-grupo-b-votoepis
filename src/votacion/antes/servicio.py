"""Versión inicial del flujo de emisión de voto de VotoEPIS."""

from src.votacion.dominio import EstadoEleccion


class ServicioVotacion:
    def __init__(self, almacen, padron_local, sistema_academico, correo):
        self.almacen = almacen
        self.padron_local = padron_local
        self.sistema_academico = sistema_academico
        self.correo = correo

    def emitir_voto(self, estudiante_id, eleccion_id, candidato_id,
                    fuente="LOCAL"):

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

        habilitado = False

        if fuente == "LOCAL":
            for intento in range(3):
                try:
                    habilitado = self.padron_local.esta_habilitado(
                        estudiante_id, eleccion_id
                    )
                    break
                except TimeoutError:
                    if intento == 2:
                        return False

        elif fuente == "ACADEMICO":
            for intento in range(3):
                try:
                    respuesta = self.sistema_academico.consultar_condicion(
                        estudiante.codigo, eleccion_id
                    )
                    habilitado = respuesta["situacion"] == "HABILITADO"
                    break
                except TimeoutError:
                    if intento == 2:
                        return False

        else:
            raise ValueError(
                f"Fuente de habilitación no soportada: {fuente}"
            )

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
