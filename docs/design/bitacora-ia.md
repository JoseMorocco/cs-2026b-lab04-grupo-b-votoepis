# Bitácora de uso de IA — VotoEPIS (Lab 05)

| # | Fecha | Herramienta | Prompt (resumen) | Propuesta obtenida | Verificación o corrección | Decisión |
|---|---|---|---|---|---|---|
| 1 | 11/10/2026 | Claude | Prompt IA 1: Proponer diagrama de clases PlantUML para el flujo de voto secreto respetando el ADR-002 (separar Participacion y Voto). | Generó el esqueleto de clases con atributos, multiplicidades y el enum de EstadoEleccion. | Se verificó que Voto no almacenara la identidad del estudiante y que se incluyeran correctamente las interfaces de los puertos. | Aceptada |
| 2 | 11/10/2026 | Claude | Prompt IA 2: Auditar el diagrama de secuencia contra el de clases verificando la regla C1 y la inclusión de `alt`, `opt` y mensajes asíncronos. | Presentó una tabla validando que cada mensaje correspondía a una operación declarada en la clase receptora. | Se revisaron los hallazgos y se confirmó que las operaciones de los repositorios coincidían exactamente con los mensajes del flujo. | Corregida |
| 3 | 11/10/2026 | Claude | Prompt IA 3: Evaluar las reglas C1–C5 sobre los cinco diagramas del diseño (clases, secuencia, estados, actividades y paquetes). | Identificó posibles errores de consistencia en nombres y supuestos ciclos en las dependencias de paquetes. | Se evaluó cada hallazgo de la IA. Se documentó un falso positivo detectado en el diagrama de paquetes, ya que la herramienta interpretó incorrectamente una flecha de dependencia unidireccional. | Aceptada |

## Anexo: prompts para ejecutar

### Prompt IA 1 — Diagrama de clases
Actúa como diseñador de software orientado a objetos. Contexto: VotoEPIS, monolito en capas definido en el Laboratorio 04. Revisa `docs/design/historia.md` y los ADR existentes. Propón un diagrama de clases PlantUML para el flujo «Emitir un voto secreto». Debe incluir al menos seis clases, atributos tipados con visibilidad, operaciones, multiplicidades en ambos extremos de las asociaciones, una enumeración para el estado de Eleccion y una interfaz para el servicio externo de correo institucional, siempre que este comportamiento esté justificado por la historia. Mantén separadas Participacion y Voto; Voto no debe almacenar la identidad del estudiante ni relacionarse con Participacion. No agregues clases sin justificación. Devuelve solo el código PlantUML y una lista breve de supuestos.

### Prompt IA 2 — Secuencia y C1
Actúa como revisor UML. Compara `docs/design/secuencia-emitir-voto.puml` con `docs/design/clases.puml`. Verifica C1: cada mensaje dirigido a un objeto debe corresponder a una operación declarada en la clase receptora. Revisa también `alt`, `loop` u `opt`, los mensajes de retorno y el mensaje asíncrono. No inventes operaciones sin justificarlas. Devuelve una tabla con mensaje, clase receptora, operación existente y corrección sugerida.

### Prompt IA 3 — Auditoría C1–C5
Actúa como revisor de diseño. Revisa los cinco diagramas de `docs/design/`: clases, secuencia, estados, actividades y paquetes. Evalúa C1–C5: operaciones de los mensajes, operaciones/eventos de las transiciones, multiplicidades, dependencias sin ciclos coherentes con ADR-001 y nombres consistentes. Para cada hallazgo indica archivo y elemento, problema, regla, corrección sugerida y nivel de certeza. No reescribas los diagramas. El equipo verificará cada hallazgo y registrará explícitamente cualquier falso positivo confirmado.