"""Pruebas específicas de patrones del Laboratorio 07 (E2 a E5)."""

from uuid import uuid4
import pytest

from src.votacion.decoradores import ConReintentos
from src.votacion.dominio import (
    Candidato,
    Eleccion,
    EstadoEleccion,
    Estudiante,
    PadronPort,
)
from src.votacion.elegibilidad import FabricaFuentes, PadronLocalAdapter
from src.votacion.eventos import PublicadorEventos
from src.votacion.externos import (
    AlmacenElectoralSimulado,
    CorreoSimulado,
    PadronLocalSimulado,
    SistemaAcademicoSimulado,
)
from src.votacion.ia import (
    AdaptadorLLMSimulado,
    AsistenteReglamento,
    ClienteLLMFalso,
    ConCache,
    SinIndicacionesDeVoto,
    SinResultadosInventados,
)
from src.votacion.servicio import ServicioVotacion


class PadronAlternativo(PadronPort):
    """Nueva estrategia simulada para comprobar extensibilidad (Open/Closed)."""

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
        lambda: PadronAlternativo({(estudiante_id, eleccion_id)}),
    )

    servicio = ServicioVotacion(
        almacen, local, academico, correo, fabrica=fabrica
    )

    resultado = servicio.emitir_voto(
        estudiante_id, eleccion_id, candidato_id, fuente="ALTERNATIVO"
    )

    assert resultado is True
    assert len(almacen.votos) == 1
    assert len(almacen.participaciones) == 1
    assert local.llamadas == 0
    assert academico.llamadas == 0


def test_state_transiciones_validas():
    eleccion = Eleccion(
        uuid4(),
        "Elección EPIS",
        EstadoEleccion.CONFIGURADA,
        [Candidato(uuid4(), "Lista A", "Agrupación A")],
    )

    eleccion.abrir(padron_cargado=True)
    assert eleccion.estado == EstadoEleccion.ABIERTA

    eleccion.cerrar()
    assert eleccion.estado == EstadoEleccion.CERRADA

    eleccion.iniciar_escrutinio(autorizado=True)
    assert eleccion.estado == EstadoEleccion.ESCRUTADA

    eleccion.publicar_resultados(
        acta_firmada=True, totales_verificados=True
    )
    assert eleccion.estado == EstadoEleccion.PUBLICADA


def test_state_impide_transicion_invalida():
    eleccion = Eleccion(
        uuid4(), "Elección EPIS", EstadoEleccion.CONFIGURADA
    )

    with pytest.raises(ValueError):
        eleccion.cerrar()

    assert eleccion.estado == EstadoEleccion.CONFIGURADA


def test_state_exige_condiciones_para_abrir():
    eleccion = Eleccion(
        uuid4(),
        "Elección EPIS",
        EstadoEleccion.CONFIGURADA,
        [Candidato(uuid4(), "Lista A", "Agrupación A")],
    )

    with pytest.raises(ValueError, match="padrón"):
        eleccion.abrir(padron_cargado=False)

    assert eleccion.estado == EstadoEleccion.CONFIGURADA


def test_e4_decorator_reintenta_solo_timeouts():
    estudiante, eleccion = uuid4(), uuid4()
    cliente = PadronLocalSimulado(
        {(estudiante, eleccion)}, fallos_iniciales=2
    )
    puerto = ConReintentos(PadronLocalAdapter(cliente), intentos=3)
    assert puerto.esta_habilitado(estudiante, eleccion) is True
    assert cliente.llamadas == 3


def test_e4_decorator_no_reintenta_rechazo():
    cliente = PadronLocalSimulado()
    puerto = ConReintentos(PadronLocalAdapter(cliente))
    assert puerto.esta_habilitado(uuid4(), uuid4()) is False
    assert cliente.llamadas == 1


def test_e4_observer_permite_suscriptores_sin_modificar_publicador():
    avisos = []

    class OtroSuscriptor:
        def actualizar(self, nombre, datos):
            avisos.append((nombre, datos))

    publicador = PublicadorEventos()
    publicador.suscribir("participacion_registrada", OtroSuscriptor())
    publicador.publicar(
        "participacion_registrada", {"eleccion_id": uuid4()}
    )
    assert len(avisos) == 1
    assert "candidato_id" not in avisos[0][1]


def _asistente(respuesta):
    cliente = ClienteLLMFalso(respuesta)
    proveedor = ConCache(AdaptadorLLMSimulado(cliente))
    cadena = SinIndicacionesDeVoto(SinResultadosInventados())
    return (
        AsistenteReglamento(
            proveedor, cadena, "Reglas de ejemplo, no oficiales."
        ),
        cliente,
    )


def test_e5_respuesta_valida_y_cache():
    asistente, cliente = _asistente(
        "El reglamento exige identificación vigente."
    )
    assert (
        asistente.responder("¿Qué necesito?")
        == "El reglamento exige identificación vigente."
    )
    assert (
        asistente.responder("¿Qué necesito?")
        == "El reglamento exige identificación vigente."
    )
    assert cliente.llamadas == 1


@pytest.mark.parametrize(
    "respuesta",
    [
        "Vota por la Lista A.",
        "La lista A es la ganadora.",
    ],
)
def test_e5_guardrails_bloquean_salida_invalida(respuesta):
    asistente, _ = _asistente(respuesta)
    with pytest.raises(ValueError, match="Guardrail"):
        asistente.responder("¿Cuál es el reglamento?")