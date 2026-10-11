# Bitácora de uso de IA — VotoEPIS (Lab 05)

| # | Fecha | Herramienta | Prompt (resumen) | Propuesta obtenida | Verificación o corrección | Decisión |
|---|---|---|---|---|---|---|
| 4 | 11/10/2026 | Claude | Prompt IA 4: Proponer la máquina de estados Mermaid de Eleccion con las operaciones de clases.puml como transiciones (C2). | Generó un stateDiagram-v2 con los cinco estados de EstadoEleccion, estado inicial y final, y guardas en las transiciones. | Se verificó que los estados coincidieran con la enumeración, que cada transición usara una operación declarada en Eleccion y que no hubiera estados sin salida, salvo el final. Se ajustaron las guardas. | Corregida |
| 5 | 11/10/2026 | Claude | Prompt IA 5: Modelar en PlantUML el proceso «Escrutinio y firma del acta» con particiones, decisiones y ejecución paralela. | Propuso un diagrama de actividades con tres particiones, dos decisiones y un fork para el conteo de votos y participaciones. | Se verificó la coherencia con E3 (la publicación solo ocurre tras la firma del acta) y que el conteo no vinculara Participacion con Voto (ADR-002). Se validó el flujo con un compañero. | Corregida |

## Anexo: prompts para ejecutar

### Prompt IA 4 — Máquina de estados
Actúa como diseñador de software orientado a objetos. Contexto: VotoEPIS, monolito en capas definido en el Laboratorio 04. Entidad: Eleccion, con la enumeración EstadoEleccion (CONFIGURADA, ABIERTA, CERRADA, ESCRUTADA, PUBLICADA) y las operaciones declaradas en `docs/design/clases.puml`: verificarEstado(), abrir(), cerrar(), iniciarEscrutinio() y publicarResultados(). Propón una máquina de estados en Mermaid (stateDiagram-v2) con cinco o más estados, el estado inicial [*], al menos un estado final y dos o más guardas entre corchetes. Nombra cada transición con la operación de la clase que la provoca (C2). No agregues estados que no estén en la enumeración. Devuelve solo el código Mermaid y una lista breve de supuestos.

### Prompt IA 5 — Diagrama de actividades
Actúa como analista de procesos de software. Contexto: VotoEPIS, historia HU-01 y ADR-001, ADR-002 y ADR-003 del proyecto. Modela en PlantUML con particiones (|Partición|) el proceso «Escrutinio y firma del acta». Debe incluir tres o más particiones (Comité electoral, Sistema VotoEPIS, Auditor), dos o más decisiones (if / else) y una ejecución paralela (fork / end fork). El flujo debe ser coherente con la máquina de estados de Eleccion: la publicación de resultados solo ocurre con el acta firmada. El conteo no debe relacionar Participacion con Voto. No agregues pasos fuera del alcance del MVP. Devuelve solo el código PlantUML y una lista breve de supuestos.
