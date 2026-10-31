# ADR-006: Restricción UNIQUE y transacción relacional para integridad de emisión (Iteración 1 ADD)

* **Fecha:** 31/10/2026
* **Estado:** Aceptado (validado en prototipo SQL local; adaptador PostgreSQL pendiente)

## Contexto
Ante el escenario de crecimiento de VotoEPIS a **25 000 votantes en 8 horas con auditoría externa**[cite: 54, 60], el escenario prioritario **S1 (Seguridad / Integridad, prioridad H,H)** exige que, frente a dos emisiones solapadas de un mismo votante habilitado para la misma elección, el sistema acepte la primera y rechace el **100 % de los intentos duplicados** sin registrar un segundo voto[cite: 54, 60]. 

En la versión del Laboratorio 07 (`AlmacenElectoralSimulado`), la verificación previa `existe_participacion()` seguida de `registrar_emision()` en memoria carece de una restricción de base de datos real frente a solicitudes concurrentes (*check-then-act*)[cite: 60]. Se requiere refinar el límite entre lógica y datos del componente **Votación** respetando las restricciones **R-01** (1 mes), **R-02** (3 integrantes), **R-03** (tecnologías conocidas) y **R-04** (presupuesto bajo en un único VPS)[cite: 54, 60], así como el estilo de monolito en capas (**ADR-001**) y el modelo relacional (**ADR-002**)[cite: 60].

## Alternativas evaluadas
1. **Alternativa A — Exclusión mutua con bloqueo en memoria alrededor de consulta y escritura:** Evita el intercalado dentro de un único proceso Python, pero no garantiza unicidad entre múltiples workers o procesos independientes ni constituye persistencia durable[cite: 60]. *(No seleccionada)*[cite: 60].
2. **Alternativa B — Restricción `UNIQUE(estudiante_id, eleccion_id)` y transacción atómica participación/voto en la BD relacional:** Delega el arbitraje final de unicidad al motor relacional dentro de la misma unidad transaccional que inserta en `participacion` (con identidad) y `voto` (sin identidad)[cite: 56, 60]. *(Seleccionada)*[cite: 60].
3. **Alternativa C — Cola de mensajería y servicio separado con deduplicación distribuida:** Desacopla la recepción, pero confirmar la recepción en cola no confirma el voto, exige infraestructura adicional y viola **ADR-001** y **R-01/R-02/R-04** sin que la carga promedio (0,87 req/s) lo justifique[cite: 60]. *(Rechazada)*[cite: 60].

## Decisión
Adoptar la **Alternativa B**: materializar la restricción `UNIQUE(estudiante_id, eleccion_id)` en la tabla `participacion` y ejecutar la inserción de `participacion` y `voto` dentro de una única transacción en la base de datos relacional[cite: 60]. Cuando ocurre una colisión de unicidad (`IntegrityError`), la transacción se revierte sin insertar el segundo voto y se registra un evento `INTENTO_DUPLICADO` sin incluir el `candidato_id`[cite: 56, 60].

## Evidencia cuantitativa
El script reproducible `fitness/simular_integridad.py` (semilla fija `20261031`, 25 000 votantes en 8 h virtuales, 50 000 solicitudes con intercalado adversarial donde dos lecturas previas observan ausencia antes de escribir) demostró los siguientes resultados[cite: 56, 60]:
* **Antes (consulta previa sin `UNIQUE`):** 0 / 25 000 duplicados rechazados (**0 %**), 50 000 votos registrados (no cumple S1)[cite: 60].
* **Después (`UNIQUE` + transacción):** 25 000 / 25 000 duplicados rechazados (**100 %**), 25 000 participaciones, 25 000 votos y 25 000 eventos `INTENTO_DUPLICADO` registrados (cumple S1 con mejora de +100 puntos porcentuales)[cite: 60].

## Consecuencias y Trade-off aceptado
* **Positivas (+):** Garantiza el cumplimiento del 100 % en **S1 (QA-01)** y preserva el secreto del voto (**S5**) al mantener separadas las tablas `participacion` y `voto` sin requerir nuevos servicios[cite: 54, 60].
* **Negativas / Trade-off aceptado (-):** El índice `UNIQUE` consume espacio adicional en disco, serializa las escrituras en conflicto sobre una misma clave y exige que el adaptador de datos distinga explícitamente un conflicto de unicidad frente a otros errores operativos de la base de datos[cite: 60].