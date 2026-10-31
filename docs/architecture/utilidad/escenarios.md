# Laboratorio 08 — E1: árbol de utilidad

## Base arquitectónica y alcance

Se revisaron `drivers.md`, ADR-001, ADR-002, ADR-003, ADR-005,
`c4/workspace.dsl`, `design/historia.md`, `design/consistencia.md`,
`design/patrones/metricas.md`, `src/votacion/`, `tests/` y las bitácoras existentes.
ADR-001 define un monolito en capas, un despliegue y una BD relacional en VPS económico.
El C4 especifica PostgreSQL 16 y modela 2 vCPU/4 GB; esto es diseño documentado,
no infraestructura medida. R-01: un mes; R-02: máximo tres integrantes;
R-03: tecnologías conocidas; R-04: presupuesto bajo, servicios de pago justificados.
No se proponen microservicios ni nueva infraestructura.

ADR-002 requiere UNIQUE(estudiante, elección) y una transacción para participación
y voto separados. ADR-003 exige acta, listado anonimizado, SHA-256 publicado fuera
de la BD y eventos con permisos de solo inserción. ADR-005 conserva Strategy,
Adapter, Factory, Decorator, State, Observer y guardrails deterministas para IA.
El código ejecutable usa `AlmacenElectoralSimulado`, listas y conjuntos;
no implementa un adaptador PostgreSQL ni demuestra concurrencia, permisos de BD
o publicación externa. `Participacion.crear` y `Voto.crear` son contratos pendientes.
Los eventos del servicio omiten el candidato y las pruebas caracterizan rollback,
secreto, duplicados, estados y extensibilidad. El correo del Observer es síncrono,
aunque HU-01 describe envío asíncrono: se registra la diferencia, sin alterar Lab 05–07.

El crecimiento a **25 000 votantes / 8 horas con auditoría externa** proviene
del enunciado Lab 08. Equivale a 0,8681 primeras emisiones/s en promedio;
no demuestra capacidad ni distribución real. Los umbrales nuevos de esta tabla
son objetivos de diseño propuestos, no compromisos previos ni mediciones.
Integridad (QA-01), disponibilidad/fiabilidad (QA-02) y auditabilidad (QA-03)
preceden a modificabilidad (QA-04). Rendimiento habilita el proceso electoral.

## Escenarios de seis partes

Prioridad = (importancia, dificultad): H alta, M media, L baja.
Importancia refleja impacto electoral; dificultad refleja incertidumbre y esfuerzo
en la arquitectura actual. No es una puntuación de implementación terminada.

| ID / atributo | Fuente | Estímulo | Entorno | Artefacto | Respuesta | Medida / objetivo | Prioridad | Justificación |
|---|---|---|---|---|---|---|---|---|
| S1 Seguridad: integridad | Cliente de un votante habilitado | Envía dos emisiones solapadas para la misma elección | Elección abierta, 25 000 votantes en 8 h; prueba adversarial de un duplicado por votante | Registro de participación y voto | Acepta una emisión y rechaza la adicional sin segundo voto | **100 % de intentos duplicados rechazados** = 100 × duplicados rechazados / intentos duplicados; denominador 25 000 | (H,H) | RF-03 / QA-01: cualquier voto adicional altera el resultado; la simulación secuencial actual no acredita exclusión concurrente. Primera iteración ADD. |
| S2 Disponibilidad: conservación | Fallo de persistencia | Interrumpe la operación entre participación y voto | Elección abierta, prueba de 100 fallos inyectados | Unidad transaccional | Revierte ambas escrituras y permite reintentar | 0 registros parciales después de 100 fallos; 100/100 reintentos válidos registrados una sola vez | (H,H) | QA-02 / ADR-002: perder participación impide ejercer el voto; requiere atomicidad y recuperación. |
| S3 Disponibilidad: continuidad | Operador de la elección | Mantiene abierta la jornada | Ventana de 28 800 s con sondeo cada segundo | Aplicación y BD en VPS único | Responde a operación sintética de habilitación y registro | ≥99,5 % de sondeos exitosos (respuesta en ≤2 s), como máximo 144 sondeos fallidos | (H,H) | QA-02: 25 000 votantes dependen del único VPS; se debe medir, sin prometer alta disponibilidad inexistente. |
| S4 Seguridad: auditabilidad | Auditor externo | Solicita verificar resultados publicados | Cierre de elección universitaria | Acta, listado anonimizado y huella externa | Entrega paquete que permita recalcular totales y SHA-256 | 100 % de resultados publicados asociados a acta y listado cuya huella coincida con copia externa; 0 diferencias de conteo | (H,M) | QA-03 / ADR-003: la auditoría externa exige comprobación independiente; se reutiliza la decisión existente. |
| S5 Seguridad: confidencialidad | Auditor de privacidad | Inspecciona votos y eventos exportados | Dataset de prueba de 25 000 emisiones | Tablas separadas y payloads Observer | Excluye identidad del voto y candidato de eventos de participación/seguridad | 0 votos con campo de identidad; 0 eventos con campo candidato_id en 25 000 emisiones | (H,M) | QA-01 / ADR-005 y HU-01: crecer no debe vincular votante y preferencia; mide campos, no anonimato frente a correlación temporal. |
| S6 Rendimiento | Clientes habilitados | Emiten votos válidos | 25 000 primeras emisiones/8 h, uniformes; concentración supuesta: 5 000 en 5 min y 20 000 en el resto | Flujo de emisión | Confirma registro | p95 de tiempo entre recepción y respuesta ≤2 s, errores técnicos ≤1 % en cada perfil | (M,H) | 0,8681/s de media y 16,6667/s en la concentración propuesta; faltan tiempos reales de BD y padrón. No sustituye la medida de integridad S1. |
| S7 Modificabilidad | Desarrollador | Añade tercera fuente de padrón | Mantenimiento con suite Lab 07 | PadronPort, adaptador y FabricaFuentes | Registra estrategia sin cambiar ServicioVotacion | 0 líneas modificadas de ServicioVotacion y 100 % de suite previa aprobada, con 1 nueva prueba de contrato | (M,L) | QA-04 / ADR-005: extensión ya prevista y caracterizada; equipo de tres necesita cambios acotados. |
| S8 Seguridad: auditabilidad de rechazo | Cliente duplicado | Reintenta una emisión ya confirmada | Elección abierta, 25 000 reintentos secuenciales de prueba | PublicadorEventos y auditoría | Registra rechazo sin preferencia electoral | 25 000/25 000 rechazos con evento INTENTO_DUPLICADO y 0 eventos con candidato_id | (H,M) | ADR-003 / ADR-005: permite justificar rechazos ante auditor externo sin revelar el voto. La durabilidad de eventos queda pendiente. |

## Revisión de prioridades con IA

En esta sesión la IA propuso inicialmente S4=(M,M), por ejecutarse al cierre.
Al contrastarlo con QA-03 y la auditoría externa del nuevo escenario se corrigió
a **(H,M)**: el momento de ejecución no reduce la importancia de verificar resultados.
Es una autocorrección de la IA; no se afirma una aprobación humana ni del equipo.
S1, S2 y S3 quedan (H,H), y S4/S5/S8 (H,M), cubriendo los atributos críticos.
S1 desempata frente a S2/S3 por el orden crítico de QA-01 en los drivers y por
permitir un experimento acotado sin comprar infraestructura.

## Generación y comprobación

Desde la raíz, con Graphviz instalado:

```powershell
dot -Tpng docs/architecture/utilidad/arbol.dot -o docs/architecture/utilidad/arbol.png
```

`arbol.dot` es la fuente del PNG; IDs, prioridades y medidas corresponden a esta tabla.
E1 establece objetivos; no declara superados S1–S8. E2 evalúa solamente S1
y propiedades auxiliares del prototipo, sin desarrollar E3–E8.
