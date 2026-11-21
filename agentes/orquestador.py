"""Orquestación actor-crítico para ISSUE-02 (variante B)."""

from pathlib import Path

from agentes.agente.herramientas import Sandbox


class Planificador:
    def planificar(self, issue):
        return [
            "Leer issue y código defectuoso.",
            "Corregir conteo para separar válidos de blancos.",
            "Ejecutar pruebas y revisar diff.",
        ]


class Ejecutor:
    def __init__(self, sandbox):
        self.sandbox = sandbox

    def aplicar_correccion(self, anterior, nuevo):
        return self.sandbox.editar_archivo(self.sandbox.editable, anterior, nuevo)


class RevisorSoloLectura:
    def __init__(self, sandbox):
        self.sandbox = sandbox

    def leer(self, ruta):
        return self.sandbox.leer_archivo(ruta)

    def ver_cambios(self):
        return self.sandbox.ver_cambios()

    def ejecutar_pruebas(self):
        return self.sandbox.ejecutar_pruebas()

    def editar(self, *args, **kwargs):
        raise PermissionError("El revisor es de solo lectura y no puede editar.")


class Critico:
    def revisar(self, diff, resultado_pruebas):
        motivos = []
        if resultado_pruebas.get("codigo") != 0:
            motivos.append("Las pruebas no pasan.")
        if "validos" not in diff and "validos" not in str(resultado_pruebas):
            # no bloquear por ausencia textual; las pruebas son la fuente
            pass
        if motivos:
            return "CAMBIOS SOLICITADOS", motivos
        return "APROBADO", []


class Orquestador:
    def __init__(self, origen, issue="ISSUE-02", max_rondas=2):
        self.origen = Path(origen).resolve()
        self.issue = issue
        self.max_rondas = max(1, min(2, max_rondas))

    def ejecutar_variante_b(self, defecto, correccion):
        sandbox = Sandbox(self.origen, issue=self.issue)
        # sembrar defecto en la copia
        (sandbox.raiz / sandbox.editable).write_text(defecto, encoding="utf-8")
        planificador = Planificador()
        ejecutor = Ejecutor(sandbox)
        revisor = RevisorSoloLectura(sandbox)
        critico = Critico()
        historial = []
        veredicto = None
        motivos = []
        for ronda in range(1, self.max_rondas + 1):
            try:
                if ronda == 1:
                    ejecutor.aplicar_correccion(defecto.strip(), correccion.strip())
                else:
                    # aplicar corrección tras feedback
                    ejecutor.aplicar_correccion(defecto.strip(), correccion.strip())
                diff = revisor.ver_cambios()
                pruebas = revisor.ejecutar_pruebas()
                veredicto, motivos = critico.revisar(diff, pruebas)
                historial.append({
                    "ronda": ronda,
                    "veredicto": veredicto,
                    "motivos": motivos,
                    "codigo_pruebas": pruebas.get("codigo"),
                })
                if veredicto == "APROBADO":
                    break
            except Exception as error:
                veredicto = "CAMBIOS SOLICITADOS"
                motivos = [str(error)]
                historial.append({"ronda": ronda, "veredicto": veredicto, "motivos": motivos, "codigo_pruebas": None})
                break
        final = {
            "issue": self.issue,
            "rondas": len(historial),
            "veredicto": veredicto,
            "motivos": motivos,
            "historial": historial,
            "sandbox": sandbox,
        }
        return final
