# Bitácora de uso de IA — VotoEPIS (Lab 05)

| # | Fecha | Herramienta | Prompt (resumen) | Propuesta obtenida | Verificación o corrección | Decisión |
|---|---|---|---|---|---|---|
| 4 | 11/10/2026 | Claude | Prompt IA 4: Proponer la máquina de estados Mermaid de Eleccion con las operaciones de clases.puml como transiciones (C2). | Generó un stateDiagram-v2 con los cinco estados de EstadoEleccion, estado inicial y final, y guardas en las transiciones. | Se verificó que los estados coincidieran con la enumeración, que cada transición usara una operación declarada en Eleccion y que no hubiera estados sin salida, salvo el final. Se ajustaron las guardas. | Corregida |

## Anexo: prompts para ejecutar

### Prompt IA 4 — Máquina de estados
Actúa como diseñador de software orientado a objetos. Contexto: VotoEPIS, monolito en capas definido en el Laboratorio 04. Entidad: Eleccion, con la enumeración EstadoEleccion (CONFIGURADA, ABIERTA, CERRADA, ESCRUTADA, PUBLICADA) y las operaciones declaradas en `docs/design/clases.puml`: verificarEstado(), abrir(), cerrar(), iniciarEscrutinio() y publicarResultados(). Propón una máquina de estados en Mermaid (stateDiagram-v2) con cinco o más estados, el estado inicial [*], al menos un estado final y dos o más guardas entre corchetes. Nombra cada transición con la operación de la clase que la provoca (C2). No agregues estados que no estén en la enumeración. Devuelve solo el código Mermaid y una lista breve de supuestos.


