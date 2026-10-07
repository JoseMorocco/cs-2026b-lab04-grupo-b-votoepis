# ADR-001: Estilo arquitectónico: monolito en capas
- Estado: Aceptado
- Fecha: 2026-10-01
- Decisores: Luque Guevara Fernando Gerson, Morocco Saico Jose Manuel, Hilacondo Begazo Emanuel David

## Contexto
VotoEPIS es un sistema de elección digital de delegados estudiantiles de la EPIS. Debe gestionar el padrón (RF-01), verificar la habilitación (RF-02), registrar un voto por estudiante (RF-03), contar automáticamente (RF-04) y publicar resultados y acta (RF-05, RF-06).

El atributo crítico es la seguridad e integridad (QA-01), seguido de fiabilidad (QA-02), auditabilidad (QA-03) y mantenibilidad (QA-04). Las restricciones son: MVP en producción en 1 mes (R-01), equipo de máximo 3 integrantes (R-02), tecnologías que el equipo ya conoce (R-03) y presupuesto bajo (R-04).

Se evaluaron tres alternativas con una matriz ponderada (criterios: seguridad e integridad 30 %, tiempo de implementación 25 %, mantenibilidad 20 %, complejidad operativa 15 %, costo 10 %).

## Alternativas consideradas
1. **Monolito en capas (puntaje 4.30):** una sola aplicación con capas de presentación, lógica y datos, y una base de datos relacional.
2. **Monolito modular hexagonal con registro de eventos inmutable (puntaje 3.70):** un solo despliegue, con módulos separados por puertos y adaptadores y un registro con hash encadenado.
3. **Serverless / BaaS (puntaje 3.50):** funciones y servicios de backend administrados.

## Decisión
Usaremos un **monolito en capas** (presentación, lógica de negocio y datos) con una base de datos relacional y un único despliegue en un VPS económico. Las reglas de votación, conteo y acta vivirán en la capa de lógica, separadas de la interfaz y del acceso a datos.

## Consecuencias
- Positivas: es la única alternativa que permite cumplir el plazo de 1 mes (R-01) con un equipo de 3 personas (R-02); usa tecnologías conocidas (R-03); tiene un solo despliegue y bajo costo operativo (R-04); cubre QA-01 con un puntaje de 4 sobre 5 mediante restricciones en la base de datos y validación en la capa de lógica.
- Negativas / riesgos: la mantenibilidad es menor (3 sobre 5) que en la alternativa hexagonal, y el acoplamiento entre capas puede crecer si no se respeta la disciplina de dependencias; el escalado es vertical, no por módulo; la auditabilidad (QA-03) no cuenta con un registro inmutable, por lo que dependerá del acta y de los resultados verificables, y deberá revisarse si el sistema pasa de MVP a uso real.
