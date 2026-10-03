# ADR-002: Base de datos relacional (PostgreSQL) con participación y voto separados
- Estado: Aceptado
- Fecha: 2026-10-01
- Decisores: Luque Guevara Fernando Gerson, Morocco Saico Jose Manuel, Hilacondo Begazo Emanuel David

## Contexto
El sistema debe registrar un solo voto por estudiante (RF-03) y rechazar el 100 % de los intentos duplicados (escenario QA-01). Cada voto válido debe quedar registrado correctamente (escenario QA-02) y los resultados deben poder verificarse con un acta (QA-03, RF-06). El plazo es de 1 mes (R-01), el equipo es de 3 integrantes (R-02), debe usar tecnologías conocidas (R-03) y el presupuesto es bajo (R-04). La arquitectura elegida es un monolito en capas (ADR-001).

## Alternativas consideradas
1. **Base de datos relacional (PostgreSQL):** esquema fijo, transacciones ACID y restricciones de unicidad.
2. **Base de datos documental (por ejemplo, MongoDB):** documentos flexibles, sin esquema rígido.

## Decisión
Usaremos **PostgreSQL** como única base de datos del sistema. La unicidad del voto se garantizará con una restricción `UNIQUE (id_estudiante, id_eleccion)` en la tabla de participación. El registro de participación y el voto se guardarán en una sola transacción, en tablas separadas: la tabla de votos no almacenará la identidad del estudiante, para proteger la confidencialidad del voto.

## Consecuencias
- Positivas: la restricción de unicidad hace que el rechazo de votos duplicados lo garantice la base de datos y no solo el código (QA-01); las transacciones evitan votos a medias (QA-02); el conteo se obtiene con consultas SQL directas y repetibles (RF-04, QA-03); es software libre y corre en un VPS económico (R-04).
- Negativas / riesgos: el esquema rígido exige migraciones si cambian las reglas de la elección; el escalado es principalmente vertical; separar participación y voto impide reconstruir quién votó por quién (es lo deseado), pero complica la depuración de errores; se asume que el equipo ya conoce SQL y PostgreSQL (R-03), lo que debe confirmarse.
