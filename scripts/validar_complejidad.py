"""Control de complejidad ciclomática para el Lab 07 de VotoEPIS."""

import sys
from pathlib import Path

from radon.complexity import cc_visit
from radon.visitors import Class, Function


LIMITE = 10
RAIZ_PROYECTO = Path(__file__).resolve().parents[1]


def validar(directorio: Path) -> int:
    """Devuelve 0 si cumple, 1 si excede el límite y 2 ante un error."""
    if not directorio.is_dir():
        print(f"ERROR: no existe el directorio {directorio}")
        return 2

    total = 0
    infracciones = []

    for archivo in sorted(directorio.rglob("*.py")):
        relativo = archivo.relative_to(directorio)

        # La versión ingenua es evidencia histórica de E1.
        if "antes" in relativo.parts:
            continue

        try:
            codigo = archivo.read_text(encoding="utf-8")
            bloques = cc_visit(codigo)
        except (OSError, UnicodeError, SyntaxError) as error:
            print(f"ERROR al analizar {archivo}: {error}")
            return 2

        for bloque in bloques:
            elementos = []

            if isinstance(bloque, Class):
                elementos = [
                    (f"{bloque.name}.{metodo.name}", metodo)
                    for metodo in bloque.methods
                ]
                
            elif isinstance(bloque, Function) and not bloque.is_method:
                elementos = [(bloque.name, bloque)]

            for nombre, funcion in elementos:
                total += 1
                complejidad = funcion.complexity

                print(
                    f"{relativo}:{funcion.lineno} "
                    f"{nombre} -> CC={complejidad}"
                )

                if complejidad > LIMITE:
                    infracciones.append(
                        (relativo, nombre, complejidad)
                    )

    if total == 0:
        print("ERROR: no se encontraron funciones o métodos.")
        return 2

    print(f"\nElementos analizados: {total}")
    print(f"Límite permitido: {LIMITE}")

    if infracciones:
        print("\nFALLO: complejidad máxima superada.")

        for archivo, nombre, complejidad in infracciones:
            print(
                f"  {archivo}::{nombre}: "
                f"CC={complejidad} > {LIMITE}"
            )

        return 1

    print("\nOK: ninguna función o método supera el límite.")
    return 0


if __name__ == "__main__":
    destino = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else RAIZ_PROYECTO / "src" / "votacion"
    )

    sys.exit(validar(destino))
