# ADR-010: Arquitectura del sistema agéntico de VotoEPIS
- Estado: Aceptado
- Fecha: 2026-11-21
- Decisores: Equipo VotoEPIS

## Contexto

El Laboratorio 10 requiere agentes que resuelvan issues acotados con trazas auditables, límites explícitos y supervisión humana. El sistema debe poder inspeccionar y proponer cambios sin otorgarle acceso de escritura al repositorio de origen ni autonomía para entregar cambios.

## Alternativas consideradas

1. **Agente libre con herramientas generales:** descartado porque el modelo podría exceder el alcance del issue o escribir fuera de los archivos permitidos.
2. **Coordinación multiagente para todos los issues:** descartada como opción predeterminada porque añade rondas y contexto de coordinación innecesarios para tareas pequeñas; se conserva el patrón actor-crítico para el caso de ISSUE-02 que necesita planificación y revisión.
3. **Memoria persistente externa compartida:** descartada porque el ejercicio usa historial acotado por sesión y evidencia local; no hay requisito de retener contexto entre ejecuciones.
4. **Edición directa del repositorio con aprobación al final:** descartada porque una revisión posterior no revierte por sí sola una escritura fuera del sandbox.

## Decisión

Usaremos un **agente acotado de uso de herramientas**. El modelo devuelve decisiones JSON que pasan por contrato y política antes de invocar herramientas; el ejecutor opera sobre la copia temporal del sandbox.

| Dimensión | Decisión |
|---|---|
| Arquetipo | Agente de uso de herramientas con respuestas JSON sujetas a contrato. |
| Coordinación | ReAct de un agente como flujo predeterminado; actor-crítico para ISSUE-02, que necesita planificación y revisión. |
| Herramientas | Lectura de archivos, edición de un archivo permitido, pruebas del issue, inspección de cambios y, cuando aplica, mapa y notas del repositorio. |
| Memoria | Historial transitorio de la sesión y artefactos locales (trazas y notas del sandbox); sin almacenamiento externo persistente. |
| Límites | Contexto de hasta 100 000 caracteres, respuesta del modelo de hasta 16 000 bytes y 12 pasos por ejecución. Contrato y política validan la forma, argumentos, rutas y acciones permitidas. |
| Rol humano | Aprobación interactiva exacta (`s` o `n`) antes de cada edición. Ejecutor, revisor, colaborador y gobernador supervisan etapas manuales; el programa no automatiza su promoción. El agente no puede hacer commit, push, etiquetar ni entregar. |

La traza JSONL registra decisiones, aprobaciones, resultados, rechazos y bloqueos.

## Consecuencias

- **Positivas:** las acciones quedan sujetas a un contrato, a la política del sandbox y a límites medibles; cada edición tiene un punto de aprobación humana y la traza permite revisar el recorrido.
- **Negativas / riesgos:** tareas que excedan los límites requieren una nueva sesión o intervención humana; la aprobación por edición puede ralentizar cambios iterativos; la memoria de la sesión no permite recuperar automáticamente contexto de ejecuciones anteriores.
- **Operativas:** el revisor debe comprobar el diff y las pruebas, y el gobernador conserva la decisión de cierre y entrega; una traza no identifica al aprobador ni almacena su justificación.
