# Laboratorio 08 — E4: iteración 3 ADD 3.0 (S4, auditabilidad/seguridad)

**Estado:** paquete y verificador probados con datos sintéticos; publicación externa pendiente. **Prioridad:** (H,M). **Evidencia:** [`evidencias/auditoria.json`](evidencias/auditoria.json), script `fitness/simular_auditoria.py`.

## Paso 1. Revisar entradas

- Crecimiento: 25 000 votantes y auditoría externa del proceso electoral.
- [E1, S4](../utilidad/escenarios.md): **100 % de resultados publicados asociados a acta + listado verificable + huella que coincide con copia externa, con 0 diferencias de conteo**.
- ADR-001: monolito en capas, equipo de tres, plazo de un mes y VPS económico.
- ADR-002: voto no contiene identificador de estudiante.
- ADR-003: acta con totales, listado anonimizado y SHA-256 publicado fuera de la BD; logs solo inserción (todavía diseño, no infraestructura activa).

## Paso 2. Objetivo

Producir un paquete verificable del escrutinio sintético de **25 000 votos**: acta, listado de votos sin identidad de estudiantes, totales recalculables y SHA-256 canónico. El auditor ha de detectar alteraciones tanto del listado como del conteo publicado.

## Paso 3. Elegir elemento a refinar

Responsabilidades de cierre y publicación de actas dentro del monolito: servicio de escrutinio/publicación y capa de datos. `src/votacion` aún no implementa un exportador de actas productivo, por lo que se agrega **un prototipo en `fitness/`**, no un endpoint real.

## Paso 4. Conceptos de diseño candidatos

| Alternativa | Beneficio | Trade-off | Evaluación |
|---|---|---|---|
| A. Publicar solo totales de candidatos | Ligero y simple | Auditor depende de confianza en la BD; no recalcula ni compara | **Rechazada**: 0/1 resultados verificables |
| B. Acta + listado anónimo + SHA-256 copiado fuera del paquete | Recuento y verificación de integridad por tercero, sin revelar identidad en exportación | Más almacenamiento y publicación; protege frente a modificaciones posteriores a la huella, no demuestra anonimato frente a correlación de metadatos | **Elegida**, conforme a ADR-003 |
| C. Blockchain / ledger distribuido | Puede reforzar trazabilidad | Operación, complejidad y coste sin necesidad demostrada | Rechazada por R-01/R-02/R-04 |

## Paso 5. Instanciar responsabilidades

- `generar_votos()`: 25 000 votos **sintéticos**, con `eleccion_id` y `candidato_id`; sin campo del estudiante.
- `preparar_paquete()`: crea `acta`, `listado` ordenado y cadena SHA-256 del JSON compacto UTF-8 con claves ordenadas.
- Valor `huella_externa`: la prueba **simula** una copia mantenida por el auditor, inalterada cuando se modifica el paquete.
- `verificar()`: recalcula hash y totales; valida tamaño, elección y campos permitidos.
- `tests/test_fitness.py`: comprueba paquete, 25 000 votos, 0 diferencias y detección de adulteración.

## Paso 6. Bosquejo arquitectónico

```text
BD → Exportador de listado anónimo → Verificador de totales → Acta + SHA-256
                                                            │
                                            publicación externa del hash [PENDIENTE]
                                                            │
Auditor externo → obtiene listado + acta + hash externo → compara y recalcula
```

No se añade otro servicio ni se modifica el despliegue del ADR-001. El canal público/correo independiente es **requisito de implementación futura**, no está creado por esta simulación.

## Paso 7. Análisis y evidencia

```bash
python -m fitness.simular_auditoria
python -m pytest -q tests/test_fitness.py
```

| Medida S4 | Antes: solo totales | Después: acta + listado + hash simulado |
|---|---:|---:|
| Votos sintéticos | 25 000 | 25 000 |
| Resultados verificables / resultados publicados | 0/1 | **1/1 (100 %)** |
| Diferencias de conteo en paquete válido | No auditable | **0** |
| Cambio de candidato en el listado detectado | No verificable | **Sí** |
| Alteración de un total publicada detectada | No verificable | **Sí** |
| Votos con campo `estudiante_id` | No aplica | **0** |
| Cumple S4 en el prototipo | No | **Sí, condicionado** |

**Límite central:** la huella «externa» se entrega a la función como cadena retenida por la prueba; no se publica en un portal ni se envía a un comité real. Solo queda acreditado que un auditor con una copia confiable **puede** detectar modificaciones. Para afirmar S4 en producción faltan: exportación real desde PostgreSQL, firma/autorización del acta, publicación de la huella en canal independiente, control de acceso y prueba de auditoría por tercero. Tampoco se prueba anonimato frente a correlación estadística o de tiempos.

**Decisión y riesgo residual:** mantener ADR-003; si E3 reporta manipulación de resultados como riesgo crítico, esta iteración es mitigación parcial y exige publicación externa efectiva antes de considerarlo cerrado.
