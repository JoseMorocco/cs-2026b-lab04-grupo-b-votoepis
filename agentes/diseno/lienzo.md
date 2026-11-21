# Lienzo de diseño de VotoEPIS

## 1. Agente o flujo de trabajo

Se elige un agente para explorar un issue, localizar su causa y proponer una corrección pequeña con pruebas. El orden de inspección depende de las observaciones. El registro del voto, la habilitación y la publicación de resultados requieren un flujo fijo con reglas de dominio, transacciones y permisos verificables. La ejecución electoral debe ser determinista y auditable.

## 2. Arquetipo

ReAct acotado para mantenimiento de software. Cada decisión contiene una justificación breve, una acción estructurada o una respuesta final. El agente observa el resultado antes de decidir el siguiente paso. El primer objetivo es ISSUE-01 de la demostración aislada, cuyo resultado se comprueba con una aserción de unicidad por elección.

## 3. Herramientas

Lectura de archivos de demostración, issue y pruebas, edición exacta de un fragmento de codigos.py, ejecución de la prueba fija de ISSUE-01 y consulta de diferencias. El proceso de pruebas usa argumentos fijos y el intérprete actual. El agente no recibe una consola de comandos generales. Las pruebas permanecen protegidas frente a edición.

## 4. Memoria

Historial de corto plazo con objetivo, decisiones validadas y observaciones reales de herramientas. Las respuestas originales aceptadas o rechazadas se preservan como bytes UTF-8 y se referencian desde una traza JSONL. El historial tiene límites de tamaño y pasos. Las notas persistentes quedan para E4.

## 5. Coordinación

Un agente único en E2 reduce el contexto y permite estudiar la exploración de ISSUE-01. E5 podrá añadir gestor y actor-crítico con revisor de solo lectura y un máximo de dos rondas. Esta preparación no ejecuta ni mide esa coordinación.

## 6. Rol humano

Un integrante transporta el contexto al asistente y pega su decisión original. Revisa el diff final y la evidencia de pytest, retira el xfail únicamente de la prueba del issue efectivamente resuelto y decide si aplicar la corrección al repositorio. El contrato valida las respuestas antes de cualquier herramienta.

## 7. Control

Máximo de 12 decisiones por sesión, incluidas las rechazadas, y límites de lectura y salida. El agente opera en una copia temporal creada por el ejecutor desde archivos permitidos. Solo codigos.py es editable. Se rechazan rutas absolutas, escapes, enlaces y escrituras en tests. La política no permite ejecutar scripts ni comandos elegidos por el modelo. La terminación, los bloqueos y los resultados se registran. Una respuesta final no acredita por sí sola la resolución.

## Procedencia y alcance

La guía del Lab 10 propone los tres errores de VotoEPIS en su tabla 14. La implementación histórica identifica estudiantes por UUID, rechaza candidatos ajenos y no modela un horario programado de cierre. Los tres defectos se siembran explícitamente en agentes/demo/ y sus reglas son contratos locales de demostración. Se mantienen independientes de src/votacion/.

Se encontró la guía docente v2 y se consultaron sus páginas 9–12 y 16–18. La búsqueda local en el semestre, Descargas y adjuntos no localizó el paquete Python del mini framework. La preparación de E2 será una implementación propia basada en los requisitos de la guía, pendiente de cotejo con ese recurso.
