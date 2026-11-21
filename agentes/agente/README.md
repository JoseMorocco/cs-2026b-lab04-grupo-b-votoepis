# Preparación del agente interactivo de ISSUE-01

Implementación propia en Python 3.12 basada en los requisitos de E2 de la guía docente. El paquete del mini framework no se encontró en las ubicaciones locales consultadas. Falta cotejar esta preparación con ese recurso. E2 requiere una sesión real con ModeloInteractivo y transporte humano de las decisiones.

Desde la raíz del repositorio, usa el entorno Python del proyecto con pytest, radon y las dependencias ya declaradas en prompts/criterios/requirements.txt.

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests agentes/pruebas_agente
.\.venv\Scripts\python.exe -m agentes.agente --contexto
.\.venv\Scripts\python.exe -m agentes.agente --sesion agentes/trazas/issue-01-sesion-01
```

El contexto mostrado por la consola incluye el objetivo, el contrato JSON completo, el catálogo y el historial. Copia el contexto completo al asistente elegido, pide una decisión y pega su respuesta literal en la consola. Termina el pegado con una línea que contenga solo FIN. El separador no forma parte de la respuesta. Cada lectura de consola conserva el contenido de las líneas y usa LF entre ellas. Los campos exigidos son motivo, accion, args y respuesta.

Las herramientas leer_archivo y editar_archivo requieren los argumentos documentados en el contexto. ejecutar_pruebas y ver_cambios usan args vacío. La acción final requiere args vacío y una respuesta con la evidencia observada. El contrato rechaza texto libre, herramientas inventadas y argumentos incompatibles. Se guardan también las respuestas rechazadas, sin repararlas, y consumen el presupuesto de 12 pasos.

La copia temporal contiene únicamente codigos.py, la prueba de ISSUE-01 y su enunciado. El agente solo puede editar codigos.py mediante sustitución exacta de un fragmento único. Se valida un subconjunto de Python del ejemplo para excluir importaciones, llamadas ajenas y decoradores. pytest se ejecuta con argumentos fijos, timeout de 30 segundos y sin plugins externos. Se verifica la huella de la prueba antes de ejecutarla.

La política restringe las herramientas del prototipo. La copia temporal y el filtro AST no constituyen un aislamiento de procesos del sistema operativo. Ejecuta este prototipo con una cuenta sin credenciales ni datos sensibles, en el entorno controlado del laboratorio.

Cada sesión nueva guarda contexto por paso, decisiones originales, traza.jsonl, cambios.diff y trayectoria.mmd. No se aplican cambios al repositorio de origen. La respuesta final expresa la conclusión del asistente. El humano debe contrastarla con el resultado de pytest y revisar el diff. La copia temporal se elimina al terminar y el diff queda disponible para revisión.

Para regenerar el diagrama desde una traza real existente:

```powershell
.\.venv\Scripts\python.exe -m agentes.agente.traza agentes/trazas/issue-01-sesion-01/traza.jsonl agentes/trazas/issue-01-sesion-01/regenerado.mmd
```

Tras una sesión real exitosa, el equipo puede aplicar el diff revisado a agentes/demo/codigos.py, retirar el xfail de tests/test_issue_01.py y verificar la suite. ISSUE-02 e ISSUE-03 conservan su marcador. El segundo commit requiere esa evidencia real. Las pruebas unitarias en carpetas temporales son verificaciones de infraestructura y no acreditan una ejecución interactiva de E2.
