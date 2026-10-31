# Laboratorio 08 — E4: iteración 2 ADD 3.0 (S2, disponibilidad/fiabilidad)

**Estado:** experimento ejecutado en SQLite local; diseño pendiente de implementar en PostgreSQL. **Prioridad:** (H,H). **Evidencia:** [`evidencias/recuperacion.json`](evidencias/recuperacion.json), script `fitness/simular_recuperacion.py`.

## Paso 1. Revisar entradas

- Caso VotoEPIS: **25 000 votantes en 8 h con auditoría externa**.
- [E1, S2](../utilidad/escenarios.md): falla entre participación y voto; ante 100 fallos, **0 registros parciales y 100/100 reintentos recuperados**.
- ADR-001: monolito en capas y un VPS, equipo máximo de 3, 1 mes y bajo presupuesto.
- ADR-002: participación/voto separados, restricción única y transacción ACID.
- E2 probó unicidad del voto (S1), no el despliegue PostgreSQL ni fallos de proceso real.

## Paso 2. Objetivo

Para 100 estudiantes sintéticos, inducir una excepción tras insertar participación, antes de insertar voto; reintentar cada emisión una vez con la falla desactivada. Objetivo S2: **cero participaciones huérfanas y 100 reintentos válidos aceptados**, sin duplicidad.

## Paso 3. Elegir elemento a refinar

Límite lógica/datos: `registrar_emision(estudiante_id, eleccion_id, candidato_id)`, donde participan las tablas `participacion` (con identificador) y `voto` (sin identificador). Se preservan `ServicioVotacion`, el patrón Observer y la separación del secreto electoral.

## Paso 4. Conceptos de diseño candidatos

| Alternativa | Beneficio | Trade-off | Evaluación |
|---|---|---|---|
| A. Guardar ambas filas con commits separados | Implementación simple | Un fallo después del primer commit bloquea el reintento por UNIQUE | **Rechazada**: deja 100/100 participaciones huérfanas |
| B. Una transacción ACID con ROLLBACK | El par se guarda completo o no se guarda | Bloqueos y costo de transacciones; requiere gestión cuidadosa de excepciones | **Elegida**: 0 huérfanas y 100 reintentos |
| C. Cola de votos pendientes en proceso | Permite diferir escritura | No recupera persistencia tras reinicio sin almacenamiento durable; complejidad extra | Rechazada por R-01/R-04 y falta de evidencia de necesidad |

No se estimaron precios ni rendimiento del VPS. La alternativa B **reafirma una decisión ya tomada en ADR-002**: la simulación no implica una nueva implementación productiva.

## Paso 5. Instanciar responsabilidades e interfaces

- `ServicioVotacion`: valida elección y habilitación; solo indica éxito cuando finaliza la transacción.
- Adaptador PostgreSQL **por implementar**: inicia transacción, escribe participación y voto, hace COMMIT conjunto; ante error, ROLLBACK y propaga fallos inesperados. La colisión UNIQUE se maneja como duplicado.
- `fitness/simular_recuperacion.py`: contrasta dos `INSERT` con commits independientes contra un bloque `with db` de SQLite para el mismo conjunto de fallas.
- `tests/test_fitness.py::test_ff03_s2_cero_parciales_y_cien_reintentos`: conserva la garantía en CI del prototipo.

## Paso 6. Vista esquemática (refinamiento del contenedor de datos)

```text
Estudiante → Aplicación VotoEPIS → ServicioVotacion → Adaptador de datos
                                                         │
                                              BEGIN TRANSACTION
                                              INSERT participacion (UNIQUE)
                                              INSERT voto (sin estudiante)
                                              ├── éxito → COMMIT
                                              └── fallo → ROLLBACK → reintento
```

El C4 del Lab 06 mantiene «Aplicación VotoEPIS → Base de datos»; esta iteración no agrega servicios. La actualización formal de `workspace.dsl` y su ADR pertenecen a E6.

## Paso 7. Analizar resultado y validar

Comandos desde la raíz:

```bash
python -m fitness.simular_recuperacion
python -m pytest -q tests/test_fitness.py
```

| Medida S2 | Antes: commits separados | Después: transacción |
|---|---:|---:|
| Errores forzados entre escrituras | 100 | 100 |
| Participaciones huérfanas al final | 100 | **0** |
| Reintentos válidos aceptados | 0/100 | **100/100** |
| Votos correctamente registrados | 0 | **100** |
| Cumple S2 en prototipo | No | **Sí** |

**Supuestos y límites:** 100 electores distintos y habilitados; la falla es una excepción de aplicación después del primer INSERT; SQLite en memoria, ejecución secuencial y sin caídas de energía. Los resultados son evidencia del **mecanismo transaccional** local, no de la disponibilidad real, recuperación de un VPS o durabilidad de PostgreSQL. No acredita S3 (99,5 % durante 8 h).

**Decisión y riesgo residual:** mantener transacción y UNIQUE de ADR-002; implementar y verificar después con PostgreSQL bajo fallos concurrentes y de red. Un VPS único sigue siendo punto único de falla.
