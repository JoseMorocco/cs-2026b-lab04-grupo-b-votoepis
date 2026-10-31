# ADR-008: Paquete de escrutinio con listado anónimo canónico y huella SHA-256 externa (Iteración 3 ADD)

* **Fecha:** 31/10/2026
* **Estado:** Aceptado (verificador probado en CI; canal de publicación externa pendiente)

## Contexto
Con el crecimiento a **25 000 votantes y la incorporación de una auditoría externa**, el escenario **S4 (Seguridad / Auditabilidad, prioridad H,M)** exige que el **100 % de los resultados publicados** estén asociados a un acta electoral, un listado anonimizado de votos y una huella criptográfica `SHA-256` que coincida con una copia externa, arrojando **0 diferencias de conteo** al recalcularse de forma independiente[cite: 54, 62]. Simultáneamente, el escenario **S5 (Confidencialidad, prioridad H,M)** exige **0 votos con campo de identidad del estudiante** en las exportaciones[cite: 54, 62].

## Alternativas evaluadas
1. **Alternativa A — Publicar únicamente los totales agregados por candidato:** Ligero de implementar, pero obliga al auditor externo a confiar ciegamente en la base de datos sin poder recalcular el escrutinio ni detectar manipulaciones. *(Rechazada: 0 % de resultados verificables)*.
2. **Alternativa B — Paquete verificable (acta + listado de votos anónimo canónico + huella `SHA-256` contrastable con copia externa):** Exporta cada voto únicamente con `eleccion_id` y `candidato_id` en formato JSON canónico (UTF-8, claves ordenadas, sin espacios), calcula su hash `SHA-256` en el acta y permite al auditor recalcular totales y verificar integridad contra la huella publicada fuera de la BD. *(Seleccionada, reafirma ADR-003)*.
3. **Alternativa C — Red Blockchain / ledger distribuido para almacenar los votos:** Aporta trazabilidad criptográfica, pero introduce alta complejidad operativa, nuevos nodos y costos que infringen **R-01, R-02 y R-04** sin necesidad demostrada[cite: 62]. *(Rechazada por sobreingeniería)*[cite: 62].

## Decisión
Adoptar la **Alternativa B**: al cierre de la elección, el módulo de escrutinio y auditoría genera un paquete compuesto por el `acta` (`eleccion_id`, `total_votos`, `totales` por candidato y `sha256`) y el `listado` anónimo de votos. La huella `SHA-256` se calcula sobre la representación JSON canónica del listado y debe remitirse a un canal externo independiente (correo institucional del comité/auditor o portal público estático)[cite: 55, 62].

## Evidencia cuantitativa
El prototipo `fitness/simular_auditoria.py` y las *fitness functions* `test_ff04_s4_auditoria_integra_25000_votos` y `test_ff05_s4_rechaza_modificacion_de_acta` en `tests/test_fitness.py` evaluaron 25 000 votos sintéticos:
* **Antes (solo totales):** **0 %** de resultados verificables independientemente[cite: 55, 62].
* **Después (paquete acta + listado canónico + SHA-256 externo):** **100 % (1/1)** de resultados verificables, **0 diferencias de conteo**, **0 votos con campo `estudiante_id`** (cumple S5), y **100 % de detección** tanto ante la alteración de un voto individual en el listado como ante la modificación de un total en el acta[cite: 55, 58, 62].

## Consecuencias y Trade-off aceptado
* **Positivas (+):** Permite auditoría externa matemática e independiente (**QA-03 / S4**) preservando la confidencialidad de los campos exportados (**QA-01 / S5**) dentro del mismo monolito (**ADR-001**)[cite: 54, 62].
* **Negativas / Trade-off aceptado (-):** Incrementa el tamaño del artefacto de cierre (exportación de 25 000 registros JSON) y su seguridad real queda condicionada a que la publicación de la huella `SHA-256` se realice efectivamente en un canal externo fuera del control del administrador de la base de datos[cite: 62].