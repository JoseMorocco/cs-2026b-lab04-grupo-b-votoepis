# ADR-003: Auditoría y seguridad: acta verificable con huella publicada y bitácora de eventos
- Estado: Aceptado
- Fecha: 2026-10-01
- Decisores: Luque Guevara Fernando Gerson, Morocco Saico Jose Manuel, Hilacondo Begazo Emanuel David

## Contexto
Los resultados deben poder comprobarse de manera independiente (QA-03): el escenario exige que el 100 % de los resultados publicados esté asociado a un acta. El sistema debe contar los votos automáticamente (RF-04), publicar los resultados (RF-05) y generar el acta (RF-06). La seguridad e integridad es el atributo crítico (QA-01), incluido el rechazo y registro de los intentos de voto duplicado.

El ADR-001 eligió un monolito en capas, que no incluye un registro de eventos inmutable. La crítica adversarial a la alternativa hexagonal mostró que un hash encadenado guardado en la misma base de datos no basta como garantía de auditoría, porque quien controle la base puede recalcular la cadena. Las restricciones son el plazo de 1 mes (R-01), el equipo de 3 integrantes (R-02) y el presupuesto bajo (R-04). El ADR-002 define que los votos se guardan sin la identidad del estudiante.

## Alternativas consideradas
1. **Acta verificable con huella publicada fuera de la base de datos:** el acta incluye los totales por candidato y una huella SHA-256 del listado de votos; el listado anonimizado se publica junto al acta.
2. **Registro de eventos inmutable con hash encadenado** (propio de la alternativa hexagonal): cada voto y cada evento se encadenan con hashes en la base de datos.
3. **Solo registros (logs) de la aplicación y de la base de datos:** sin acta con huella ni exportación de votos para terceros.

## Decisión
Usaremos la **alternativa 1**. Al cerrar la elección, el sistema generará el acta con los totales por candidato, la huella SHA-256 del listado anonimizado de votos y la fecha de cierre, y publicará el listado junto al acta para que un auditor recalcule el conteo y la huella por su cuenta. La huella se publicará también en un canal distinto de la base de datos (por ejemplo, el portal público y el correo del comité). Además, mantendremos una tabla de eventos de seguridad (intentos de voto duplicado rechazados y accesos del comité electoral) a la que la aplicación solo podrá insertar, sin permisos de actualización ni borrado.

## Consecuencias
- Positivas: cumple el escenario de QA-03, porque cada resultado publicado queda asociado a un acta y puede verificarse con el listado y la huella; la huella publicada fuera de la base de datos evita el problema señalado en la crítica adversarial; es viable en el plazo de R-01 con un equipo de 3 (R-02) y no requiere servicios de pago (R-04); el registro de intentos duplicados respalda QA-01.
- Negativas / riesgos: solo detecta alteraciones al cierre de la elección, no durante ella; el administrador de la base de datos sigue siendo un punto de confianza hasta que se publique la huella; la tabla de eventos protegida por permisos es más débil que un registro inmutable; si el sistema pasa de MVP a uso real, deberá evaluarse el hash encadenado de la alternativa 2.
