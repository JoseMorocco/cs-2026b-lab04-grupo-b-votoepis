# Revisión de Consistencia (Reglas C1-C5)

| Regla | Hallazgo de la IA | Verificación del equipo |
|---|---|---|
| C1 | La operación `verificarEstado()` se invoca en el diagrama de secuencia, pero la IA indica que falta en la clase `Eleccion`. | **Falso positivo:** La operación SÍ existe en la clase `Eleccion` dentro de `clases.puml`. La IA no la procesó correctamente por un error de lectura de sintaxis. Se rechaza el hallazgo. |
| C4 | La IA reportó que el paquete "votacion depende de auditoria". | Correcto: Se respeta el ADR-001 ya que es una dependencia unidireccional (no cíclica). Se acepta el flujo. |
| C5 | Los nombres en Python usan `snake_case` (ej. `obtener_correo`), mientras que en UML usan `camelCase`. | Convención estándar de Python. Aceptable, equivalencia documentada. |