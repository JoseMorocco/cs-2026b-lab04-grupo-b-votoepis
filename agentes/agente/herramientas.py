"""Herramientas con copia temporal, pruebas fijas, edición restringida, mapa y notas."""

import ast
import difflib
import os
from hashlib import sha256
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from agentes.agente.politica import (
    ISSUE_CONFIG, EDITABLE, LECTURAS, ruta_segura, validar_codigo,
)


class Sandbox:
    def __init__(self, origen, issue="ISSUE-01", editable=None, lecturas=None, prueba=None):
        self.origen = origen.resolve()
        config = ISSUE_CONFIG.get(issue, ISSUE_CONFIG["ISSUE-01"])
        self.issue = issue
        self.editable = editable or config["editable"]
        self.lecturas = set(lecturas) if lecturas else set(config["lecturas"])
        self.prueba = prueba or config["prueba"]
        self.issue_file = config.get("issue", "issues/ISSUE-01.md")
        self.temporal = tempfile.TemporaryDirectory(prefix="votoepis-lab10-")
        self.raiz = Path(self.temporal.name).resolve()
        try:
            for ruta in sorted(self.lecturas):
                fuente = ruta_segura(self.origen, ruta, self.lecturas)
                destino = self.raiz / ruta
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(fuente, destino)
            self.original = (self.raiz / self.editable).read_text(encoding="utf-8")
            self.test_hash = sha256((self.raiz / self.prueba).read_bytes()).hexdigest()
        except Exception:
            self.cerrar()
            raise

    def cerrar(self):
        self.temporal.cleanup()

    def _segura(self, ruta):
        return ruta_segura(self.raiz, ruta, self.lecturas | {"notas.md"})

    def leer_archivo(self, ruta):
        return self._segura(ruta).read_text(encoding="utf-8")[:12000]

    def editar_archivo(self, ruta, anterior, nuevo):
        if ruta != self.editable:
            raise ValueError("Solo se permite editar el archivo permitido de esta copia.")
        archivo = self._segura(ruta)
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
        prueba = self._segura(self.prueba)
        if sha256(prueba.read_bytes()).hexdigest() != self.test_hash:
            raise ValueError("La prueba protegida fue alterada.")
        comando = [sys.executable, "-m", "pytest", "--runxfail", "-q", self.prueba]
        proceso = subprocess.run(
            comando, cwd=self.raiz, capture_output=True, timeout=30,
            env={"PYTHONIOENCODING": "utf-8", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        )
        return {
            "comando": f"python -m pytest --runxfail -q {self.prueba}",
            "codigo": proceso.returncode,
            "salida": (proceso.stdout + proceso.stderr).decode("utf-8", errors="replace")[:16000],
        }

    def ver_cambios(self):
        actual = (self.raiz / self.editable).read_text(encoding="utf-8")
        return "".join(difflib.unified_diff(
            self.original.splitlines(keepends=True), actual.splitlines(keepends=True),
            fromfile="original/" + self.editable, tofile="sandbox/" + self.editable,
        ))

    def mapa_repo(self):
        lineas = []
        firmas = []
        max_depth = 5
        max_files = 200
        max_chars = 12000
        contador = 0
        for raiz_dir, dirs, archivos in os.walk(self.raiz, followlinks=False):
            rel = Path(raiz_dir).relative_to(self.raiz)
            depth = len(rel.parts)
            if depth > max_depth:
                dirs[:] = []
                continue
            # evitar enlaces
            dirs[:] = [d for d in dirs if not (Path(raiz_dir) / d).is_symlink()]
            for nombre in sorted(archivos):
                if contador >= max_files:
                    break
                ruta = Path(raiz_dir) / nombre
                if ruta.is_symlink():
                    continue
                relpath = (rel / nombre).as_posix() if str(rel) != "." else nombre
                try:
                    st = ruta.stat()
                except OSError:
                    continue
                if st.st_size > 200000:
                    lineas.append(f"{relpath} (omitido por tamaño)")
                    contador += 1
                    continue
                lineas.append(relpath)
                if nombre.endswith(".py"):
                    try:
                        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
                        for nodo in arbol.body:
                            if isinstance(nodo, (ast.ClassDef, ast.FunctionDef)):
                                args = ast.unparse(nodo.args) if hasattr(nodo, "args") else ""
                                firmas.append(f"{relpath}: {nodo.__class__.__name__} {nodo.name}({args})")
                    except (SyntaxError, OSError, UnicodeError):
                        firmas.append(f"{relpath}: <error de análisis>")
                contador += 1
            if contador >= max_files:
                break
        salida = "ÁRBOL PERMITIDO:\n" + "\n".join(lineas) + "\n\nFIRMAS:\n" + "\n".join(firmas)
        return salida[:max_chars]

    def anotar(self, texto):
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("La nota debe ser texto no vacío.")
        if len(texto) > 2000:
            raise ValueError("La nota excede el límite de 2000 caracteres.")
        ruta = self.raiz / "notas.md"
        actual = ruta.read_text(encoding="utf-8") if ruta.exists() else ""
        if len(actual) + len(texto.strip()) + 1 > 20000:
            raise ValueError("Se excede el tamaño total de notas.")
        with ruta.open("a", encoding="utf-8", newline="\n") as f:
            f.write(texto.strip() + "\n")
        return "Nota registrada."

    def leer_notas(self):
        ruta = self.raiz / "notas.md"
        if not ruta.exists():
            return ""
        return ruta.read_text(encoding="utf-8")[:20000]

    def ejecutar(self, accion, args):
        funciones = {
            "leer_archivo": self.leer_archivo,
            "editar_archivo": self.editar_archivo,
            "ejecutar_pruebas": self.ejecutar_pruebas,
            "ver_cambios": self.ver_cambios,
            "mapa_repo": self.mapa_repo,
            "anotar": self.anotar,
            "leer_notas": self.leer_notas,
        }
        return funciones[accion](**args)
