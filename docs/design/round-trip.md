# Round-trip: Diagrama de Diseño vs Código (VotoEPIS)

| Diferencia observada | Causa | Acción |
|---|---|---|
| No aparecen las asociaciones exactas ni las multiplicidades (ej. `Eleccion "1" o-- "1..*" Candidato`). | `pyreverse` no infiere asociaciones complejas ni cardinalidades de negocio desde colecciones tipadas en Python. | Ninguna: limitación esperada de la herramienta. El diagrama de diseño UML se mantiene como fuente de verdad (C3). |
| Las interfaces (`CorreoPort`, `VotoRepositorio`, etc.) figuran gráficamente como clases normales y los métodos como abstractos. | Python implementa interfaces heredando de la clase `ABC` (Abstract Base Class). El adaptador lanza `NotImplementedError`. | Aceptable en Python; se documenta la equivalencia arquitectónica. |
| Nombres en `snake_case` en los métodos generados (ej. `enviar_confirmacion`) frente a `camelCase` en el diagrama original (`enviarConfirmacion`). | Convención nativa de escritura en Python recomendada por PEP 8. | Aceptable; se documenta la equivalencia de nombres respetando la Regla C5. |