"""Herramientas con copia temporal, pruebas fijas y edición restringida."""

import difflib
from hashlib import sha256
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from agentes.agente.politica import EDITABLE, LECTURAS, ruta_segura, validar_codigo


class Sandbox:
    def __init__(self, origen):
        self.temporal = tempfile.TemporaryDirectory(prefix="votoepis-lab10-")
        self.raiz = Path(self.temporal.name).resolve()
        self.origen = origen.resolve()
        try:
            for ruta in sorted(LECTURAS):
                fuente = ruta_segura(self.origen, ruta)
                destino = self.raiz / ruta
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(fuente, destino)
            self.original = (self.raiz / EDITABLE).read_text(encoding="utf-8")
            self.test_hash = sha256((self.raiz / "tests/test_issue_01.py").read_bytes()).hexdigest()
        except Exception:
            self.cerrar()
            raise

    def cerrar(self):
        self.temporal.cleanup()

    def leer_archivo(self, ruta):
        return ruta_segura(self.raiz, ruta).read_text(encoding="utf-8")[:12000]

    def editar_archivo(self, ruta, anterior, nuevo):
        if ruta != EDITABLE:
            raise ValueError("Solo se permite editar codigos.py.")
        archivo = ruta_segura(self.raiz, ruta)
        texto = archivo.read_text(encoding="utf-8")
        if texto.count(anterior) != 1:
            raise ValueError("El fragmento anterior debe aparecer exactamente una vez.")
        texto = texto.replace(anterior, nuevo, 1)
        if len(texto) > 12000:
            raise ValueError("El archivo excede el tamaño permitido.")
        validar_codigo(texto)
        archivo.write_text(texto, encoding="utf-8", newline="\n")
        return "Edición aplicada a la copia temporal."

    def ejecutar_pruebas(self):
        prueba = ruta_segura(self.raiz, "tests/test_issue_01.py")
        if sha256(prueba.read_bytes()).hexdigest() != self.test_hash:
            raise ValueError("La prueba protegida fue alterada.")
        comando = [sys.executable, "-m", "pytest", "--runxfail", "-q", "tests/test_issue_01.py"]
        proceso = subprocess.run(
            comando, cwd=self.raiz, capture_output=True, timeout=30,
            env={"PYTHONIOENCODING": "utf-8", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        )
        return {
            "comando": "python -m pytest --runxfail -q tests/test_issue_01.py",
            "codigo": proceso.returncode,
            "salida": (proceso.stdout + proceso.stderr).decode("utf-8", errors="replace")[:16000],
        }

    def ver_cambios(self):
        actual = ruta_segura(self.raiz, EDITABLE).read_text(encoding="utf-8")
        return "".join(difflib.unified_diff(
            self.original.splitlines(keepends=True), actual.splitlines(keepends=True),
            fromfile="original/" + EDITABLE, tofile="sandbox/" + EDITABLE,
        ))

    def ejecutar(self, accion, args):
        funciones = {
            "leer_archivo": self.leer_archivo,
            "editar_archivo": self.editar_archivo,
            "ejecutar_pruebas": self.ejecutar_pruebas,
            "ver_cambios": self.ver_cambios,
        }
        return funciones[accion](**args)
