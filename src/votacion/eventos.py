from collections import defaultdict


class PublicadorEventos:
    def __init__(self):
        self._suscriptores = defaultdict(list)

    def suscribir(self, nombre_evento, suscriptor):
        self._suscriptores[nombre_evento].append(suscriptor)

    def publicar(self, nombre_evento, datos):
        for suscriptor in self._suscriptores[nombre_evento]:
            suscriptor.actualizar(nombre_evento, dict(datos))


class ConfirmacionCorreo:
    def __init__(self, correo):
        self.correo = correo

    def actualizar(self, nombre_evento, datos):
        if nombre_evento == "participacion_registrada" and datos.get("correo"):
            self.correo.enviar(
                datos["correo"],
                "Confirmación de participación en VotoEPIS",
                "Tu participación en la elección fue registrada.",
            )


class AuditoriaSeguridad:
    def __init__(self, eventos_seguridad):
        self.eventos_seguridad = eventos_seguridad

    def actualizar(self, nombre_evento, datos):
        if nombre_evento == "intento_duplicado":
            self.eventos_seguridad.append({
                "tipo": "INTENTO_DUPLICADO",
                "estudiante_id": datos["estudiante_id"],
                "eleccion_id": datos["eleccion_id"],
            })
