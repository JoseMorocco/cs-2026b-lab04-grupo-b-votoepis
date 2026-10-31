"""E2: intercalado determinista de dos emisiones por votante, con SQL real.

Ejecutar desde la raíz: python -m fitness.simular_integridad
SQLite es un instrumento local de prueba; la decisión de producción sigue siendo
PostgreSQL. No se miden latencia, durabilidad ni concurrencia real del motor.
"""

import argparse
import csv
import io
import json
import random
import sqlite3
from pathlib import Path


PARAMETROS = {"votantes": 25_000, "horas": 8, "semilla": 20261031,
              "duplicados_por_votante": 1, "eleccion": 1}
EVIDENCIAS = Path(__file__).resolve().parents[1] / "docs/architecture/add/evidencias"


class AlmacenPrototipo:
    """Participación y voto en una transacción; unicidad opcional para comparar."""

    def __init__(self, unico):
        self.db = sqlite3.connect(":memory:")
        restriccion = ", UNIQUE(estudiante_id, eleccion_id)" if unico else ""
        self.db.executescript(f"""
            CREATE TABLE participacion (
                estudiante_id INTEGER NOT NULL, eleccion_id INTEGER NOT NULL
                {restriccion});
            CREATE INDEX busqueda ON participacion(estudiante_id, eleccion_id);
            CREATE TABLE voto (
                eleccion_id INTEGER NOT NULL, candidato_id INTEGER NOT NULL);
            CREATE TABLE evento (
                estudiante_id INTEGER NOT NULL, eleccion_id INTEGER NOT NULL,
                tipo TEXT NOT NULL);
        """)

    def existe(self, estudiante, eleccion):
        return self.db.execute(
            "SELECT 1 FROM participacion WHERE estudiante_id=? AND eleccion_id=?",
            (estudiante, eleccion),
        ).fetchone() is not None

    def registrar(self, estudiante, eleccion, candidato, fallo=False):
        try:
            with self.db:
                self.db.execute("INSERT INTO participacion VALUES (?, ?)",
                                (estudiante, eleccion))
                if fallo:
                    raise RuntimeError("Fallo inyectado entre escrituras")
                self.db.execute("INSERT INTO voto VALUES (?, ?)", (eleccion, candidato))
        except sqlite3.IntegrityError as error:
            if error.sqlite_errorname != "SQLITE_CONSTRAINT_UNIQUE":
                raise
            with self.db:
                self.db.execute("INSERT INTO evento VALUES (?, ?, ?)",
                                (estudiante, eleccion, "INTENTO_DUPLICADO"))
            return False
        return True

    def cantidades(self):
        return {
            tabla: self.db.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            for tabla in ("participacion", "voto", "evento")
        }

    def cerrar(self):
        self.db.close()


def agenda(votantes, horas, semilla):
    """Tiempo virtual uniforme; orden de identidades permutado con semilla fija."""
    if votantes < 1 or horas <= 0:
        raise ValueError("Votantes y horas deben ser positivos")
    identidades = list(range(1, votantes + 1))
    random.Random(semilla).shuffle(identidades)
    return [(i * horas * 3600 / votantes, identidad)
            for i, identidad in enumerate(identidades)]


def comparar(votantes=25_000, horas=8, semilla=20261031):
    llegadas = agenda(votantes, horas, semilla)
    resultados = []
    for modo, unico in (("antes", False), ("despues", True)):
        almacen = AlmacenPrototipo(unico)
        aceptados = rechazados = 0
        try:
            for _, estudiante in llegadas:
                # A consulta, B consulta, A escribe, B escribe. Las dos lecturas
                # previas ven ausencia: intercalado adversarial de check-then-act.
                previa_a = almacen.existe(estudiante, 1)
                previa_b = almacen.existe(estudiante, 1)
                if previa_a or previa_b:
                    raise AssertionError("La agenda repitió una identidad")
                aceptados += almacen.registrar(estudiante, 1, 1 + estudiante % 3)
                segundo = almacen.registrar(estudiante, 1, 1 + estudiante % 3)
                aceptados += segundo
                rechazados += not segundo
            resultados.append({
                "modo": modo, "votantes": votantes, "horas": horas,
                "solicitudes": 2 * votantes, "intentos_duplicados": votantes,
                "duplicados_rechazados": rechazados,
                "porcentaje_duplicados_rechazados": 100 * rechazados / votantes,
                "emisiones_aceptadas": aceptados, **almacen.cantidades(),
                "cumple_s1": rechazados == votantes,
            })
        finally:
            almacen.cerrar()
    return {"parametros": {**PARAMETROS, "votantes": votantes, "horas": horas,
                           "semilla": semilla}, "resultados": resultados}


def serializar(resultado):
    salida = io.StringIO(newline="")
    filas = resultado["resultados"]
    escritor = csv.DictWriter(salida, fieldnames=list(filas[0]), lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(filas)
    return {"resultados.json": json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
            "resultados.csv": salida.getvalue()}


def graficar(resultado, destino):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    filas = resultado["resultados"]
    fig, ax = plt.subplots(figsize=(8, 4.8), layout="constrained")
    valores = [r["porcentaje_duplicados_rechazados"] for r in filas]
    barras = ax.bar(["Antes: consulta previa", "Después: UNIQUE + transacción"],
                    valores, color=["#b64e49", "#287f6d"])
    ax.bar_label(barras, labels=[f"{v:.0f} %" for v in valores], padding=5)
    ax.axhline(100, color="#32465c", linestyle="--", label="Objetivo S1: 100 %")
    ax.set(ylim=(0, 118), ylabel="Intentos duplicados rechazados (%)",
           title="S1 · Integridad en el intercalado adversarial\n"
                 "25 000 votantes / 8 h virtuales · 25 000 duplicados")
    ax.legend(loc="upper left")
    fig.savefig(destino, dpi=150, metadata={"Software": "VotoEPIS Lab08 E2"})
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=EVIDENCIAS)
    parser.add_argument("--verificar", action="store_true",
                        help="Compara dos ejecuciones y la evidencia guardada sin sobrescribir")
    args = parser.parse_args()
    resultado = comparar()
    archivos = serializar(resultado)
    if args.verificar:
        if archivos != serializar(comparar()):
            raise SystemExit("FALLO: ejecuciones distintas")
        for nombre, contenido in archivos.items():
            if (args.salida / nombre).read_bytes() != contenido.encode("utf-8"):
                raise SystemExit(f"FALLO: evidencia distinta: {nombre}")
        print("Reproducibilidad OK: dos ejecuciones y JSON/CSV guardados idénticos")
    else:
        args.salida.mkdir(parents=True, exist_ok=True)
        for nombre, contenido in archivos.items():
            (args.salida / nombre).write_text(contenido, encoding="utf-8", newline="\n")
        graficar(resultado, args.salida / "integridad.png")
    print(archivos["resultados.csv"], end="")
    if not resultado["resultados"][1]["cumple_s1"]:
        raise SystemExit("FALLO: la táctica no cumple S1")


if __name__ == "__main__":
    main()
