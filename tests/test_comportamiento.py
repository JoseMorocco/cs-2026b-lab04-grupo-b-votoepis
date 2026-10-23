"""Pruebas de caracterización del flujo de votación."""

import importlib
from types import SimpleNamespace
from uuid import uuid4

import pytest

from src.votacion.dominio import (
    Candidato, Eleccion, EstadoEleccion, Estudiante
)
from src.votacion.externos import (
    AlmacenElectoralSimulado,
    CorreoSimulado,
    PadronLocalSimulado,
    SistemaAcademicoSimulado,
)


@pytest.fixture(params=[
    "src.votacion.antes.servicio",
    "src.votacion.servicio",
])
def modulo(request):
    return importlib.import_module(request.param)


@pytest.fixture
def caso(modulo):
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
    local = PadronLocalSimulado({(estudiante_id, eleccion_id)})
    academico = SistemaAcademicoSimulado({
        (estudiante.codigo, eleccion_id)
    })
    correo = CorreoSimulado()

    servicio = modulo.ServicioVotacion(
        almacen, local, academico, correo
    )

    return SimpleNamespace(
        servicio=servicio,
        almacen=almacen,
        local=local,
        academico=academico,
        correo=correo,
        estudiante_id=estudiante_id,
        eleccion_id=eleccion_id,
        candidato_id=candidato_id,
        estudiante=estudiante,
        eleccion=eleccion,
    )


def votar(c, fuente="LOCAL"):
    return c.servicio.emitir_voto(
        c.estudiante_id, c.eleccion_id, c.candidato_id, fuente
    )


def test_voto_valido_persiste_participacion_y_voto(caso):
    assert votar(caso) is True
    assert (caso.estudiante_id, caso.eleccion_id) in caso.almacen.participaciones
    assert len(caso.almacen.votos) == 1


def test_fuente_academica_simulada_habilita(caso):
    assert votar(caso, "ACADEMICO") is True
    assert caso.academico.llamadas == 1


def test_eleccion_cerrada_rechaza_sin_registros(caso):
    caso.eleccion.estado = EstadoEleccion.CERRADA
    assert votar(caso) is False
    assert not caso.almacen.votos
    assert not caso.almacen.participaciones


def test_estudiante_no_habilitado_rechazado(caso):
    caso.local.habilitados.clear()
    assert votar(caso) is False
    assert not caso.almacen.votos


def test_candidato_ajeno_rechazado(caso):
    caso.candidato_id = uuid4()
    assert votar(caso) is False
    assert not caso.almacen.votos


def test_voto_duplicado_se_rechaza_y_audita(caso):
    assert votar(caso) is True
    assert votar(caso) is False
    assert len(caso.almacen.votos) == 1
    assert len(caso.almacen.eventos_seguridad) == 1
    assert caso.almacen.eventos_seguridad[0]["tipo"] == "INTENTO_DUPLICADO"


def test_voto_no_contiene_identidad_del_estudiante(caso):
    assert votar(caso) is True
    voto = caso.almacen.votos[0]
    assert set(voto) == {"eleccion_id", "candidato_id"}
    assert caso.estudiante_id not in voto.values()


def test_correo_confirma_sin_revelar_candidato(caso):
    assert votar(caso) is True
    assert len(caso.correo.envios) == 1
    assert caso.correo.envios[0]["destino"] == caso.estudiante.correo_institucional
    assert str(caso.candidato_id) not in str(caso.correo.envios)


def test_sin_correo_institucional_registra_el_voto(caso):
    caso.estudiante.correo_institucional = ""
    assert votar(caso) is True
    assert caso.correo.envios == []


def test_reintento_ante_dos_timeouts_locales(caso):
    caso.local.fallos_iniciales = 2
    assert votar(caso) is True
    assert caso.local.llamadas == 3


def test_tres_timeouts_rechazan_sin_persistir(caso):
    caso.local.fallos_iniciales = 3
    assert votar(caso) is False
    assert caso.local.llamadas == 3
    assert not caso.almacen.participaciones
    assert not caso.almacen.votos


def test_falla_al_guardar_voto_revierte_participacion(caso):
    caso.almacen.fallar_guardado_voto = True
    with pytest.raises(RuntimeError, match="Falló el guardado"):
        votar(caso)
    assert not caso.almacen.participaciones
    assert not caso.almacen.votos
    assert not caso.correo.envios


def test_fuente_desconocida_no_modifica_registros(caso):
    with pytest.raises(ValueError, match="Fuente de habilitación"):
        votar(caso, "OTRA")
    assert not caso.almacen.participaciones
    assert not caso.almacen.votos


def test_eleccion_inexistente_no_modifica_registros(caso):
    caso.eleccion_id = uuid4()
    assert votar(caso) is False
    assert not caso.almacen.participaciones
    assert not caso.almacen.votos
