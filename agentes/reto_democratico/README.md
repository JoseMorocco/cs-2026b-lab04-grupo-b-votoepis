# Coordinación democrática para ISSUE-02

La revisión democrática requiere tres votos independientes de corrección, diseño y seguridad. Dos o tres votos APROBADO producen aprobación. Cero o uno producen rechazo. Se exige exactamente un voto de cada especialidad y cada voto incluye motivos y hallazgos.

Los revisores son componentes deterministas locales. Reciben un expediente inmutable con código, diff, resultado real de pytest e inventario de cambios. Cada uno evalúa su área sin conocer los votos anteriores. El orden inverso produce las mismas decisiones. Los revisores no reciben el sandbox ni herramientas de edición.

- Corrección examina el resultado de la prueba funcional existente de ISSUE-02.
- Diseño comprueba la función pública, su firma y el tamaño de la propuesta. Señala la ausencia de documentación del módulo.
- Seguridad compara los archivos modificados con el permiso de edición y aplica el filtro AST vigente del agente.

La decisión colectiva es una revisión del cambio. Los permisos de las herramientas siguen aplicándose a cada edición. Un voto de mayoría no concede permisos nuevos. La prueba de seguridad comprueba tanto el rechazo del revisor ante un expediente con cambios en tests como el bloqueo real de intentos de editar tests o introducir importaciones en el sandbox.

## Comparación con E5

Se reutiliza directamente Critico de agentes/orquestador.py como línea base. El orquestador y sus pruebas de E5 se conservan. La comparación del reto crea dos copias temporales a partir del mismo origen, siembra el defecto y aplica la misma propuesta usada en la prueba de la variante B de E5.

Se fija el origen del diff al defecto sembrado para mostrar la corrección del conteo. El origen del repositorio ya contiene la función corregida con una docstring. La propuesta de la prueba E5 tiene nueve líneas y carece de esa docstring. El ensayo vuelve a comprobar la corrección en la copia temporal y no publica ese contenido en el repositorio.

Cada modalidad ejecuta una vez la misma prueba y recopila los mismos campos de evidencia. La democrática añade dos revisiones especializadas. El contador de operaciones contabiliza las cuatro tareas de recopilación y cada llamada al revisor. No representa instrucciones de CPU ni llamadas a un modelo.

| Modalidad | Pruebas de ISSUE-02 | Revisores | Operaciones | Tiempo medido (ms) | Decisión |
| --- | --- | ---: | ---: | ---: | --- |
| Crítico individual E5 | 1 passed | 1 | 5 | 995,956 | APROBADO |
| Democrática | 1 passed | 3 | 7 | 850,131 | APROBADO, 3/3 |

Las revisiones especializadas consumieron 0,053 ms en corrección, 0,199 ms en diseño y 0,139 ms en seguridad. La diferencia de tiempo total está dominada por el arranque de pytest y las condiciones del sistema. Esta ejecución individual, siempre primero, y democrática, después, no permite estimar una mejora de rendimiento. El costo adicional observado consiste en dos llamadas de revisión y sus comprobaciones locales. No se midieron tokens ni costo monetario.

El crítico individual aprobó por el código 0 de pytest y devolvió cero motivos de rechazo. La revisión democrática añadió hallazgos explícitos sobre la cobertura limitada a dos candidatos y un blanco, la ausencia de docstring y el alcance de archivos y construcciones Python revisados. No se encontró un defecto funcional nuevo en esta corrección.

El voto mayoritario permite tolerar un desacuerdo individual y hace visibles las distintas responsabilidades. Sus límites son el catálogo fijo de verificaciones y la cobertura de la prueba heredada. Una aprobación 2/3 puede coexistir con un rechazo de seguridad. El humano debe leer ese motivo, y las herramientas conservan la política de mínimo privilegio. Los componentes Python no constituyen un aislamiento de procesos frente a código hostil.

## Evidencia y reproducción

[comparacion-01.json](evidencias/comparacion-01.json) conserva las dos salidas reales de pytest, el mismo diff, los tres votos estructurados, los tiempos y las huellas de los archivos de origen. El programa comprueba que los revisores dejan intacta la copia y que el repositorio conserva sus archivos originales. La comparación no utiliza ni reescribe las trazas históricas.

Desde la raíz del repositorio con el entorno Python existente:

```powershell
.\.venv\Scripts\python.exe -m pytest -q agentes/reto_democratico/test_democracia.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m agentes.reto_democratico.comparar --salida agentes/reto_democratico/evidencias/comparacion-02.json
```

El comando exige una ruta de salida nueva. El JSON generado procede de las ejecuciones reales. Los votos usados para probar 3/3, 2/3, 1/3 y 0/3 son exclusivamente datos unitarios y están separados del resultado del ensayo.

La validación terminó con 12 pruebas específicas aprobadas y 146 aprobadas en la suite completa. La omisión existente corresponde a la creación de symlinks sin permisos en Windows. [Pruebas específicas](evidencias/pytest-especifico.txt) · [Suite completa](evidencias/pytest-completo.txt)
