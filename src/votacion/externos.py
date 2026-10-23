"""Servicios simulados para las pruebas del Laboratorio 07."""


class PadronLocalSimulado:
    def __init__(self, habilitados=None, fallos_iniciales=0):
        self.habilitados = set(habilitados or [])
        self.fallos_iniciales = fallos_iniciales
        self.llamadas = 0

    def esta_habilitado(self, estudiante_id, eleccion_id):
        self.llamadas += 1
        if self.llamadas <= self.fallos_iniciales:
            raise TimeoutError("Padrón local no disponible")
        return (estudiante_id, eleccion_id) in self.habilitados


class SistemaAcademicoSimulado:
    def __init__(self, habilitados=None, fallos_iniciales=0):
        self.habilitados = set(habilitados or [])
        self.fallos_iniciales = fallos_iniciales
        self.llamadas = 0

    def consultar_condicion(self, codigo, eleccion_id):
        self.llamadas += 1
        if self.llamadas <= self.fallos_iniciales:
            raise TimeoutError("Sistema académico no disponible")

        situacion = (
            "HABILITADO"
            if (codigo, eleccion_id) in self.habilitados
            else "NO_HABILITADO"
        )
        return {"situacion": situacion}


class CorreoSimulado:
    def __init__(self):
        self.envios = []

    def enviar(self, destino, asunto, cuerpo):
        self.envios.append({
            "destino": destino,
            "asunto": asunto,
            "cuerpo": cuerpo,
        })


class AlmacenElectoralSimulado:
    def __init__(self, elecciones=None, estudiantes=None):
        self.elecciones = dict(elecciones or {})
        self.estudiantes = dict(estudiantes or {})
        self.participaciones = set()
        self.votos = []
        self.eventos_seguridad = []
        self.fallar_guardado_voto = False

    def existe_participacion(self, estudiante_id, eleccion_id):
        return (estudiante_id, eleccion_id) in self.participaciones

    def registrar_emision(self, estudiante_id, eleccion_id, candidato_id):
        """Simula el registro atómico de participación y voto."""
        clave = (estudiante_id, eleccion_id)

        if clave in self.participaciones:
            return False

        self.participaciones.add(clave)

        try:
            if self.fallar_guardado_voto:
                raise RuntimeError("Falló el guardado del voto")

            self.votos.append({
                "eleccion_id": eleccion_id,
                "candidato_id": candidato_id,
            })
        except Exception:
            self.participaciones.remove(clave)
            raise

        return True
