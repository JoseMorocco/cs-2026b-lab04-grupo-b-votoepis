"""E5: fitness functions de calidad; medidas S2 y S4 del árbol E1."""
from fitness.simular_recuperacion import comparar as comparar_s2
from fitness.simular_auditoria import (
    comparar as comparar_s4, generar_votos, preparar_paquete, verificar,
)


def test_ff03_s2_cero_parciales_y_cien_reintentos():
    r = comparar_s2(100)
    assert r["antes"]["registros_parciales"] == 100  # baseline de control
    assert not r["antes"]["cumple_s2"]
    assert r["despues"]["registros_parciales"] == 0
    assert r["despues"]["reintentos_aceptados"] == 100
    assert r["despues"]["cumple_s2"]


def test_ff04_s4_auditoria_integra_25000_votos():
    r = comparar_s4(25_000)
    assert r["antes"]["porcentaje_resultados_verificables"] == 0
    assert r["despues"]["porcentaje_resultados_verificables"] == 100
    assert r["despues"]["diferencias_conteo"] == 0
    assert r["despues"]["votos_con_campo_estudiante"] == 0
    assert r["despues"]["alteracion_de_voto_detectada"]
    assert r["despues"]["alteracion_de_totales_detectada"]


def test_ff05_s4_rechaza_modificacion_de_acta():
    paquete, externa = preparar_paquete(generar_votos(20))
    assert verificar(paquete, externa)
    paquete["acta"]["total_votos"] += 1
    assert not verificar(paquete, externa)
