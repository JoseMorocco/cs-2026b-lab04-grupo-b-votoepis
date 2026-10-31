# E5 — Evidencia de ejecución real (violación FF-02 detectada y revertida)

**Fecha de ejecución:** 31/10/2026.
**Rama:** `lab08/e4-e5-add-fitness`.
**Entorno local:** Python 3.14.8 en `.venv`; `pytest==9.1.1`, `radon==6.0.1`, `import-linter==2.15`.
El workflow de CI usa Python 3.12 con las mismas versiones fijadas de herramientas.

Este documento registra la ejecución efectuada en esta rama. No sustituye la
evidencia de preparación de [`salida-violacion-ast.md`](salida-violacion-ast.md).

## 1. Estado previo (sin violación)

```text
$ lint-imports
Contracts: 2 kept, 0 broken.

$ python -m pytest -q tests/test_fitness_estructura.py
2 passed in 0.01s
```

## 2. Violación inyectada temporalmente

Comando ejecutado al final de `src/votacion/elegibilidad.py`:

```bash
printf '\nfrom src.votacion.servicio import ServicioVotacion  # E5 violacion temporal FF-02\n' >> src/votacion/elegibilidad.py
```

## 3. Resultado observado con la violación

### Prueba AST

```text
$ python -m pytest -q tests/test_fitness_estructura.py
.F                                                                       [100%]
=================================== FAILURES ===================================
__________________ test_ff02_adaptadores_no_importan_servicio __________________

    def test_ff02_adaptadores_no_importan_servicio():
        for modulo in ("elegibilidad", "decoradores", "eventos", "externos"):
>           assert "src.votacion.servicio" not in dependencias_de(modulo), modulo
E           AssertionError: elegibilidad
E           assert 'src.votacion.servicio' not in {'collections.abc', 'src.votacion.dominio', 'src.votacion.servicio'}
E            +  where {'collections.abc', 'src.votacion.dominio', 'src.votacion.servicio'} = dependencias_de('elegibilidad')

tests/test_fitness_estructura.py:32: AssertionError
=========================== short test summary info ============================
FAILED tests/test_fitness_estructura.py::test_ff02_adaptadores_no_importan_servicio - AssertionError: elegibilidad
1 failed, 1 passed in 0.02s
```

Código de salida: `1`. Regla incumplida: **FF-02**.

### import-linter

```text
$ lint-imports
Analyzed 12 files, 10 dependencies.

FF-01 El dominio no depende de infraestructura ni orquestacion (ADR-001) KEPT
FF-02 Los adaptadores y eventos no conocen la orquestacion (ADR-005) BROKEN

Contracts: 1 kept, 1 broken.

FF-02 Los adaptadores y eventos no conocen la orquestacion (ADR-005)
--------------------------------------------------------------------

src.votacion.elegibilidad is not allowed to import src.votacion.servicio:

-   src.votacion.elegibilidad -> src.votacion.servicio (l.52)
```

Código de salida: `1`. Contrato incumplido: **FF-02**.

## 4. Reversión y comprobación posterior

La violación se revirtió con `git revert` del commit temporal, preservando el
historial. Tras la reversión se repitieron los comandos:

```text
$ python -m pytest -q tests/test_fitness_estructura.py
..                                                                       [100%]
2 passed in 0.01s

$ lint-imports
Analyzed 12 files, 9 dependencies.

FF-01 El dominio no depende de infraestructura ni orquestacion (ADR-001) KEPT
FF-02 Los adaptadores y eventos no conocen la orquestacion (ADR-005) KEPT

Contracts: 2 kept, 0 broken.

$ python -m pytest -q tests/
............................................................             [100%]
60 passed in 1.93s
```

## 5. Estado del PR y de GitHub Actions

La rama `lab08/e4-e5-add-fitness` se publicó en `origin`
(`https://github.com/JoseMorocco/cs-2026b-lab04-grupo-b-votoepis`), incluido el
commit temporal de violación y su `revert`. No se pudo abrir el pull request ni
observar el run rojo/verde de Actions desde este entorno porque el cliente `gh`
no está instalado y no hay credenciales de GitHub disponibles. La creación del
PR queda pendiente en el enlace que GitHub sugiere:

`https://github.com/JoseMorocco/cs-2026b-lab04-grupo-b-votoepis/pull/new/lab08/e4-e5-add-fitness`

No se afirma que el workflow haya pasado en GitHub.
