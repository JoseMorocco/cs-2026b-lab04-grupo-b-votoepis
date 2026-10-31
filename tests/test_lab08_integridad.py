"""E2: propiedades del prototipo; no afirman garantías de PostgreSQL."""

import pytest

from fitness.simular_integridad import AlmacenPrototipo, agenda, comparar, serializar


def test_s1_escala_universitaria_antes_despues_y_reproducibilidad():
    resultado = comparar()
    antes, despues = resultado["resultados"]
    assert resultado["parametros"]["votantes"] == 25_000
    assert resultado["parametros"]["horas"] == 8
    assert antes["porcentaje_duplicados_rechazados"] == 0
    assert antes["voto"] == antes["participacion"] == 50_000
    assert not antes["cumple_s1"]
    assert despues["porcentaje_duplicados_rechazados"] == 100
    assert despues["duplicados_rechazados"] == despues["evento"] == 25_000
    assert despues["voto"] == despues["participacion"] == 25_000
    assert despues["solicitudes"] == 50_000
    assert despues["cumple_s1"]
    assert serializar(resultado) == serializar(comparar())


def test_agenda_cubre_ocho_horas_sin_duplicar_votantes():
    llegadas = agenda(25_000, 8, 20261031)
    assert len({identidad for _, identidad in llegadas}) == 25_000
    assert llegadas[0][0] == 0
    assert llegadas[-1][0] == pytest.approx(28_800 - 28_800 / 25_000)
    assert llegadas == sorted(llegadas)
    assert llegadas != agenda(25_000, 8, 42)


@pytest.mark.parametrize("votantes,horas", [(0, 8), (-1, 8), (1, 0)])
def test_agenda_rechaza_parametros_invalidos(votantes, horas):
    with pytest.raises(ValueError):
        agenda(votantes, horas, 1)


def test_rollback_permite_reintento_y_unicidad_es_por_eleccion():
    almacen = AlmacenPrototipo(True)
    try:
        for estudiante in range(100):
            with pytest.raises(RuntimeError, match="Fallo inyectado"):
                almacen.registrar(estudiante, 1, 7, fallo=True)
        assert almacen.cantidades() == {"participacion": 0, "voto": 0, "evento": 0}
        for estudiante in range(100):
            assert almacen.registrar(estudiante, 1, 7)
            assert not almacen.registrar(estudiante, 1, 8)
            assert almacen.registrar(estudiante, 2, 8)
        assert almacen.cantidades() == {"participacion": 200, "voto": 200, "evento": 100}
    finally:
        almacen.cerrar()


def test_esquema_separa_identidad_y_candidato():
    almacen = AlmacenPrototipo(True)
    try:
        assert almacen.registrar(123, 1, 7)
        assert not almacen.registrar(123, 1, 8)
        columnas_voto = {r[1] for r in almacen.db.execute("PRAGMA table_info(voto)")}
        columnas_evento = {r[1] for r in almacen.db.execute("PRAGMA table_info(evento)")}
        assert columnas_voto == {"eleccion_id", "candidato_id"}
        assert columnas_evento == {"estudiante_id", "eleccion_id", "tipo"}
        assert almacen.db.execute("SELECT candidato_id FROM voto").fetchall() == [(7,)]
    finally:
        almacen.cerrar()
