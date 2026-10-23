# E1 — Análisis de olores de código de VotoEPIS

## 1. Contexto

Se analizó la versión inicial del flujo de emisión de voto implementada en `src/votacion/antes/servicio.py`, basada en el diagrama de secuencia del Laboratorio 05.

La ejecución de `pytest` confirmó que las 14 pruebas de caracterización pasaron correctamente. Radon identificó una complejidad ciclomática de **18 (C)** en `ServicioVotacion.emitir_voto`, un promedio de **10.0 (B)** y **73 SLOC** en el archivo principal.

## 2. Olores identificados y patrones propuestos

| Código o sección | Olor detectado | Patrón propuesto | Principio SOLID | Decisión y costo |
|---|---|---|---|---|
| Condicionales `if fuente == "LOCAL"` y `elif fuente == "ACADEMICO"` | Selección rígida de proveedores | Strategy + Factory | OCP, DIP | Aceptar para E2. Agrega una interfaz y una fábrica, pero permite añadir fuentes sin modificar el servicio. |
| Llamadas `esta_habilitado()` y `consultar_condicion()` | Acoplamiento con interfaces externas diferentes | Adapter | DIP, ISP | Aceptar para E2. Requiere adaptadores, pero evita que el servicio conozca los formatos de cada proveedor. |
| Bloques `for intento in range(3)` repetidos | Duplicación de lógica de reintentos | Decorator | SRP, OCP | Reservar para E4. Agrega un envoltorio, pero centraliza los reintentos. |
| Método `emitir_voto()` con múltiples validaciones, persistencia y correo | Método largo y múltiples responsabilidades | Extracción de responsabilidades | SRP | Aceptar progresivamente. Requiere distribuir la lógica sin alterar los resultados observables. |
| Registro directo de eventos de seguridad y envío de confirmaciones | Responsabilidades de notificación acopladas al servicio | Observer | SRP, OCP | Reservar para E4. Introduce suscriptores, pero facilita incorporar auditoría y notificaciones sin modificar el flujo principal. |
| Creación de proveedores mediante múltiples fábricas relacionadas | Posible sobreingeniería | Abstract Factory | OCP, DIP | **Rechazar.** No existen familias de productos relacionadas que justifiquen este patrón; una fábrica por registro resulta más sencilla. |

## 3. Evaluación de la propuesta rechazada

Como alternativa para manejar los proveedores, se evaluó Abstract Factory. Aunque podría organizar la creación de múltiples objetos relacionados, actualmente solo necesitamos seleccionar una fuente de habilitación y adaptar su interfaz.

Por ello, se prefiere una Factory basada en registro junto con Strategy y Adapter. Incorporar Abstract Factory aumentaría la cantidad de clases sin resolver un problema adicional.

## 4. Conclusión

El principal problema de la versión inicial es la concentración de responsabilidades en `emitir_voto()`, cuya complejidad alcanza 18. Se decidió aplicar primero Strategy, Adapter y Factory, conservando las pruebas de caracterización. Los patrones restantes se incorporarán progresivamente según las necesidades del flujo y los ejercicios siguientes.