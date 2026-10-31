# Laboratorio 08 — E5: fitness functions (guía, trazabilidad y pruebas de fallo)

## Qué se protege

| ID | Tipo | Regla / medida | Fuente | Ejecución |
|---|---|---|---|---|
| FF-01 | Estructural | `src.votacion.dominio` no importa `externos`, `servicio`, `eventos`, `elegibilidad`, `decoradores` ni `ia` | ADR-001, monolito en capas | `.importlinter` y `tests/test_fitness_estructura.py` |
| FF-02 | Estructural | Adaptadores `elegibilidad`, `decoradores`, `eventos` y `externos` no importan `servicio` (orquestador) | ADR-005, Strategy/Adapter/Decorator/Observer | `.importlinter` y `tests/test_fitness_estructura.py` |
| FF-03 | Calidad | 100 errores entre escrituras → **0 registros parciales** y **100 reintentos aceptados** | E1 S2, ADR-002 | `tests/test_fitness.py` |
| FF-04 | Calidad | 25 000 votos sintéticos: **100 % de resultados verificables**, 0 diferencias, detección de modificación del listado y acta | E1 S4, ADR-003 | `tests/test_fitness.py` |
| FF-05 | Calidad adicional | Acta con conteo alterado debe ser rechazada | E1 S4, ADR-003 | `tests/test_fitness.py` |

Se usa `root_package = src` porque **src** es el paquete raíz importado realmente (`src.votacion.*`), no el nombre `agroconecta` de la guía. Los contratos `forbidden` están documentados en Import Linter: https://import-linter.readthedocs.io/en/stable/contract_types/forbidden/.

Las reglas estructurales elegidas son **restricciones relevantes del estilo en capas** y la **separación establecida por ADR-005**; no se afirma que el repositorio tenga carpetas independientes para presentación, negocio y persistencia. Se protegen módulos existentes, no carpetas imaginarias.

## Comprobación local

```bash
python -m pip install 'pytest==9.1.1' 'radon==6.0.1' 'import-linter>=2.0,<3.0'
lint-imports
python -m pytest -v tests/test_fitness.py tests/test_fitness_estructura.py
python -m pytest -q tests/
```

**Resultados efectivamente obtenidos en el entorno de preparación:** cinco pruebas nuevas pasaron (`5 passed`). Las dos pruebas estructurales detectaron, por separado, imports inyectados, y volvieron a pasar después de restaurar los archivos. También pasaron las 56 pruebas de la suite que no dependían de `radon`. El intento de ejecutar **toda** la suite arrojó 4 fallos porque `radon` no está instalado en este entorno, no porque se observara una regresión del proyecto. No se pudo instalar `import-linter` por falta de conectividad; **su ejecución real en GitHub Actions aún debe verificarse**. El workflow instala ambos y ejecuta la suite completa.

## Reproducción en rama de fallo (NO fusionar mientras esté roja)

```bash
git checkout main
git pull
git checkout -b lab08-ff-violacion
printf '\nfrom src.votacion.servicio import ServicioVotacion  # FF-02: violacion temporal\n' >> src/votacion/elegibilidad.py
python -m pytest -q tests/test_fitness_estructura.py
# Debe FALLAR FF-02; registrar captura o salida en la documentación.
git add src/votacion/elegibilidad.py
git commit -m "test(E5): inyectar dependencia prohibida para validar fitness"
git push -u origin lab08-ff-violacion
# Abrir PR hacia main: debe fallar el job fitness.
# Después de mostrar la prueba, REVERTIR la violación:
git revert HEAD --no-edit
git push
# El mismo PR debe quedar verde. No mergear el commit que rompe el contrato.
```

El ejemplo anterior presupone que el branch nace de un `main` que **ya contiene** `.importlinter`, el workflow y las pruebas de E5. Si aún no se ha mergeado E5, crear la rama a partir de la rama de E5 y abrir el PR contra ella para la demostración, o esperar a que E5 esté en `main`.

La salida local sintetizada está en [`salida-violacion-ast.md`](salida-violacion-ast.md). **No declarar «import-linter BROKEN/KEPT comprobado»** hasta ejecutar `lint-imports` de verdad, y no declarar workflow verde hasta obtener el link del run de GitHub Actions.

## Evidencia pendiente de adjuntar por el grupo

- URL del PR de violación, con ejecución roja y luego verde: **PENDIENTE**.
- Link del job `fitness-functions-lab08` verde en PR limpio: **PENDIENTE**.
- Confirmación de los dos contratos de import-linter: **PENDIENTE**.
- Commit y responsable que revisó los resultados: **PENDIENTE**.
