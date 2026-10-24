from uuid import uuid4
import pytest

from src.votacion.decoradores import ConReintentos
from src.votacion.elegibilidad import PadronLocalAdapter
from src.votacion.eventos import PublicadorEventos
from src.votacion.externos import PadronLocalSimulado
from src.votacion.ia import (
    AdaptadorLLMSimulado, ClienteLLMFalso, ConCache,
    SinIndicacionesDeVoto, SinResultadosInventados, AsistenteReglamento,
)


def test_e4_decorator_reintenta_solo_timeouts():
    estudiante, eleccion = uuid4(), uuid4()
    cliente = PadronLocalSimulado({(estudiante, eleccion)}, fallos_iniciales=2)
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
    publicador.publicar("participacion_registrada", {"eleccion_id": uuid4()})
    assert len(avisos) == 1
    assert "candidato_id" not in avisos[0][1]


def _asistente(respuesta):
    cliente = ClienteLLMFalso(respuesta)
    proveedor = ConCache(AdaptadorLLMSimulado(cliente))
    cadena = SinIndicacionesDeVoto(SinResultadosInventados())
    return AsistenteReglamento(proveedor, cadena, "Reglas de ejemplo, no oficiales."), cliente


def test_e5_respuesta_valida_y_cache():
    asistente, cliente = _asistente("El reglamento exige identificación vigente.")
    assert asistente.responder("¿Qué necesito?") == "El reglamento exige identificación vigente."
    assert asistente.responder("¿Qué necesito?") == "El reglamento exige identificación vigente."
    assert cliente.llamadas == 1


@pytest.mark.parametrize("respuesta", [
    "Vota por la Lista A.",
    "La lista A es la ganadora.",
])
def test_e5_guardrails_bloquean_salida_invalida(respuesta):
    asistente, _ = _asistente(respuesta)
    with pytest.raises(ValueError, match="Guardrail"):
        asistente.responder("¿Cuál es el reglamento?")
