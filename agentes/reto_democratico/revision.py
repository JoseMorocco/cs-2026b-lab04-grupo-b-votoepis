"""Revisores deterministas independientes con un expediente inmutable."""

import ast
from dataclasses import asdict, dataclass
import json

from agentes.agente.politica import validar_codigo


ROLES = {"correccion", "diseno", "seguridad"}


@dataclass(frozen=True)
class Expediente:
    anterior: str
    propuesto: str
    diff: str
    pruebas_json: str
    archivos_cambiados: tuple[str, ...]
    editable: str


@dataclass(frozen=True)
class Voto:
    revisor: str
    voto: str
    motivos: tuple[str, ...]
    hallazgos: tuple[str, ...]

    def __post_init__(self):
        if self.revisor not in ROLES or self.voto not in {"APROBADO", "RECHAZADO"}:
            raise ValueError("Revisor o voto inválido.")
        if not self.motivos or any(not isinstance(m, str) or not m.strip() for m in self.motivos):
            raise ValueError("El voto requiere motivos concretos.")
        if not isinstance(self.hallazgos, tuple):
            raise ValueError("Los hallazgos deben ser una tupla.")


def decidir(revisor, problemas, hallazgos):
    return Voto(
        revisor, "RECHAZADO" if problemas else "APROBADO",
        tuple(problemas) or ("Cumple las comprobaciones de este revisor.",),
        tuple(hallazgos),
    )


class Revisor:
    def editar(self, *args, **kwargs):
        raise PermissionError("El revisor es de solo lectura y no puede editar.")


class RevisorCorreccion(Revisor):
    def revisar(self, expediente):
        pruebas = json.loads(expediente.pruebas_json)
        problemas = []
        if pruebas["codigo"] != 0:
            problemas.append("La prueba funcional de ISSUE-02 no pasa.")
        return decidir("correccion", problemas, [
            f"Prueba fija de separación de blancos y válidos: código {pruebas['codigo']}.",
            "La prueba cubre dos candidatos y un blanco; quedan otros tamaños de entrada sin cubrir.",
        ])


class RevisorDiseno(Revisor):
    def revisar(self, expediente):
        try:
            modulo = ast.parse(expediente.propuesto)
        except SyntaxError as error:
            return decidir("diseno", ["El código no es Python válido."], [str(error)])
        funciones = [n for n in modulo.body if isinstance(n, ast.FunctionDef)]
        problemas = []
        if len(funciones) != 1 or funciones[0].name != "contar":
            problemas.append("El cambio debe conservar una única función pública contar.")
        elif ast.unparse(funciones[0].args) != "votos":
            problemas.append("La firma pública contar(votos) fue alterada.")
        if len(expediente.propuesto.splitlines()) > 50:
            problemas.append("La modificación excede el alcance de esta función de demostración.")
        hallazgos = [f"Funciones de nivel superior: {len(funciones)}.",
                     f"Líneas de la propuesta: {len(expediente.propuesto.splitlines())}."]
        if ast.get_docstring(modulo) is None:
            hallazgos.append("La propuesta carece de docstring de módulo.")
        return decidir("diseno", problemas, hallazgos)


class RevisorSeguridad(Revisor):
    def revisar(self, expediente):
        problemas = []
        ajenos = sorted(set(expediente.archivos_cambiados) - {expediente.editable})
        if ajenos:
            problemas.append("Cambios fuera del permiso de edición: " + ", ".join(ajenos))
        try:
            validar_codigo(expediente.propuesto)
        except (ValueError, SyntaxError) as error:
            problemas.append(str(error))
        return decidir("seguridad", problemas, [
            "Archivos modificados: " + (", ".join(expediente.archivos_cambiados) or "ninguno"),
            "Se aplica el filtro AST vigente del agente.",
        ])


def contar_votos(votos):
    if len(votos) != 3 or {v.revisor for v in votos} != ROLES:
        raise ValueError("Se requiere un voto de cada uno de los tres revisores.")
    favorables = sum(v.voto == "APROBADO" for v in votos)
    return {
        "favorables": favorables,
        "rechazos": 3 - favorables,
        "decision": "APROBADO" if favorables >= 2 else "RECHAZADO",
        "votos": [asdict(v) for v in votos],
    }
