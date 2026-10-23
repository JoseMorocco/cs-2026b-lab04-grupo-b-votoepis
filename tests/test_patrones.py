"""Pruebas específicas de patrones del Laboratorio 07."""

from uuid import uuid4

from src.votacion.dominio import (
    Candidato,
    Eleccion,
    EstadoEleccion,
    Estudiante,
    PadronPort,
)
from src.votacion.elegibilidad import FabricaFuentes
from src.votacion.externos import (
    AlmacenElectoralSimulado,
    CorreoSimulado,
    PadronLocalSimulado,
    SistemaAcademicoSimulado,
)
from src.votacion.servicio import ServicioVotacion


class PadronAlternativo(PadronPort):
    """Nueva estrategia simulada para comprobar extensibilidad."""

    def __init__(self, habilitados):
        self._habilitados = set(habilitados)

    def esta_habilitado(self, estudiante_id, eleccion_id):
        return (estudiante_id, eleccion_id) in self._habilitados


def test_open_closed_nueva_fuente_sin_modificar_servicio():
    estudiante_id = uuid4()
    eleccion_id = uuid4()
    candidato_id = uuid4()

    estudiante = Estudiante(
        estudiante_id, "20260001", "alumno@unsa.edu.pe"
    )

    eleccion = Eleccion(
        eleccion_id,
        "Elección de delegados",
        EstadoEleccion.ABIERTA,
        [Candidato(candidato_id, "Candidata A", "Lista 1")],
    )

    almacen = AlmacenElectoralSimulado(
        {eleccion_id: eleccion},
        {estudiante_id: estudiante},
    )

    local = PadronLocalSimulado()
    academico = SistemaAcademicoSimulado()
    correo = CorreoSimulado()

    fabrica = FabricaFuentes()
    fabrica.registrar(
        "ALTERNATIVO",
        lambda: PadronAlternativo({
            (estudiante_id, eleccion_id)
        }),
    )

    servicio = ServicioVotacion(
        almacen,
        local,
        academico,
        correo,
        fabrica=fabrica,
    )

    resultado = servicio.emitir_voto(
        estudiante_id,
        eleccion_id,
        candidato_id,
        fuente="ALTERNATIVO",
    )

    assert resultado is True
    assert len(almacen.votos) == 1
    assert len(almacen.participaciones) == 1

    # Se utilizó la nueva estrategia sin consultar las anteriores.
    assert local.llamadas == 0
    assert academico.llamadas == 0
