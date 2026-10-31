"""E4 / S2: comparar escrituras separadas frente a transacción (SQLite local).

La prueba modela una excepción de aplicación entre dos INSERT. No prueba
fallos de energía, persistencia en disco, PostgreSQL ni disponibilidad 24/7.
"""
import json
import sqlite3
from pathlib import Path

EVIDENCIA = (Path(__file__).resolve().parents[1] /
            "docs/architecture/add/evidencias/recuperacion.json")


def ejecutar_caso(atomico: bool, fallos: int = 100) -> dict:
    """Cada elector falla una vez y reintenta sin falla una vez."""
    if fallos < 1:
        raise ValueError("fallos debe ser positivo")
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE participacion (
            estudiante_id INTEGER, eleccion_id INTEGER,
            UNIQUE(estudiante_id, eleccion_id));
        CREATE TABLE voto (eleccion_id INTEGER, candidato_id INTEGER);
    """)
    fallos_inyectados = reintentos_aceptados = 0
    try:
        for elector in range(fallos):
            # Simular error *después* de registrar participación y *antes* del voto.
            if atomico:
                try:
                    with db:
                        db.execute("INSERT INTO participacion VALUES (?, 1)", (elector,))
                        raise RuntimeError("falla entre escrituras")
                except RuntimeError:
                    fallos_inyectados += 1
            else:
                with db:  # antipatrón: primer commit antes de intentar voto
                    db.execute("INSERT INTO participacion VALUES (?, 1)", (elector,))
                try:
                    raise RuntimeError("falla entre escrituras")
                except RuntimeError:
                    fallos_inyectados += 1

            # Reintento válido: debe ser posible y terminar con ambas filas.
            try:
                with db:
                    db.execute("INSERT INTO participacion VALUES (?, 1)", (elector,))
                    db.execute("INSERT INTO voto VALUES (1, 7)")
                reintentos_aceptados += 1
            except sqlite3.IntegrityError as exc:
                if exc.sqlite_errorname != "SQLITE_CONSTRAINT_UNIQUE":
                    raise

        participaciones = db.execute("SELECT count(*) FROM participacion").fetchone()[0]
        votos = db.execute("SELECT count(*) FROM voto").fetchone()[0]
        huerfanas = participaciones - votos
        return {
            "modo": "transaccion" if atomico else "commits_separados",
            "fallos_inyectados": fallos_inyectados,
            "registros_parciales": huerfanas,
            "reintentos_aceptados": reintentos_aceptados,
            "reintentos_esperados": fallos,
            "participaciones": participaciones,
            "votos": votos,
            "cumple_s2": huerfanas == 0 and reintentos_aceptados == fallos,
        }
    finally:
        db.close()


def comparar(fallos: int = 100) -> dict:
    return {
        "escenario": "S2",
        "supuesto": "100 fallas de aplicación entre INSERT participación e INSERT voto",
        "antes": ejecutar_caso(False, fallos),
        "despues": ejecutar_caso(True, fallos),
    }


def main():
    resultado = comparar()
    EVIDENCIA.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCIA.write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    if resultado["antes"]["cumple_s2"] or not resultado["despues"]["cumple_s2"]:
        raise SystemExit("Resultado inesperado de S2")


if __name__ == "__main__":
    main()
