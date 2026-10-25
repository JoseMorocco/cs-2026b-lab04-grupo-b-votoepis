"""Pruebas del control automático de complejidad."""

import subprocess
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "validar_complejidad.py"
)


def crear_ejemplo(archivo, condiciones):
    archivo.parent.mkdir(parents=True, exist_ok=True)

    lineas = [
        "class Ejemplo:",
        "    def evaluar(self, valor):",
    ]

    for numero in range(condiciones):
        lineas.extend([
            f"        if valor == {numero}:",
            "            return True",
        ])

    lineas.append("        return False")
    archivo.write_text("\n".join(lineas), encoding="utf-8")


def ejecutar(directorio):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(directorio)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_acepta_complejidad_igual_a_diez(tmp_path):
    crear_ejemplo(tmp_path / "servicio.py", 9)

    resultado = ejecutar(tmp_path)

    assert resultado.returncode == 0
    assert "CC=10" in resultado.stdout


def test_rechaza_complejidad_superior_a_diez(tmp_path):
    crear_ejemplo(tmp_path / "servicio.py", 10)

    resultado = ejecutar(tmp_path)

    assert resultado.returncode == 1
    assert "CC=11" in resultado.stdout
    assert "FALLO" in resultado.stdout


def test_excluye_version_antes(tmp_path):
    crear_ejemplo(tmp_path / "antes" / "servicio.py", 15)
    crear_ejemplo(tmp_path / "servicio.py", 1)

    resultado = ejecutar(tmp_path)

    assert resultado.returncode == 0
    assert "antes" not in resultado.stdout
