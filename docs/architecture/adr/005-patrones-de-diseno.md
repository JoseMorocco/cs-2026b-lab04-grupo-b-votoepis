# ADR-005: Adopción de patrones de diseño GoF en el módulo de Votación e IA

* **Fecha:** 24/10/2026
* **Estado:** Aceptado

## Contexto
En la implementación inicial del flujo crítico de VotoEPIS (`src/votacion/antes/servicio.py`), el método `ServicioVotacion.emitir_voto()` concentraba validaciones de estado, selección de fuentes de padrón mediante condicionales `if/elif`, conversión de estructuras de datos de servicios externos, bucles duplicados de reintento ante `TimeoutError`, auditoría de intentos duplicados y envío de correos de confirmación. 

La medición con `radon` evidenció una complejidad ciclomática de **18 (rango C)** en `emitir_voto()` y un promedio de **10.0 (B)**. Cualquier cambio previsto —como alternar entre el padrón local y el Sistema Académico UNSA, añadir nuevos suscriptores de auditoría o incorporar un asistente de consultas del reglamento electoral basado en IA sin riesgo de recomendar candidaturas ni inventar resultados— obligaba a modificar directamente `ServicioVotacion`, violando los principios SRP, OCP y DIP.

## Decisión
Se decidió refactorizar el módulo `src/votacion` aplicando siete patrones de diseño GoF respaldados por una red de 14 pruebas de caracterización parametrizadas:

1. **Strategy + Adapter + Factory (basada en registro) en `elegibilidad.py`:** Se unificó la consulta de habilitación detrás de la interfaz `PadronPort` (`Strategy`), encapsulando las diferencias de interfaz en `PadronLocalAdapter` y `SistemaAcademicoAdapter` (`Adapter`) y delegando su instanciación en `FabricaFuentes` (`Factory`).
2. **Decorator en `decoradores.py` e `ia.py`:** Se extrajo la lógica transversal de tolerancia a fallos en `ConReintentos` (que reintenta hasta 3 veces únicamente ante `TimeoutError`) y el almacenamiento en memoria de respuestas repetidas del LLM en `ConCache`.
3. **State en `estados.py`:** Se implementó el ciclo de vida de `Eleccion` (`Configurada`, `Abierta`, `Cerrada`, `Escrutada`, `Publicada`) mediante subclases de `EstadoBase`, donde toda transición no permitida lanza `ValueError` por construcción.
4. **Observer en `eventos.py`:** Se desacopló el registro de seguridad (`AuditoriaSeguridad`) y la notificación por correo (`ConfirmacionCorreo`) mediante `PublicadorEventos`, garantizando que los eventos publicados nunca contengan el `candidato_id` para proteger el secreto del voto (QA-01).
5. **Chain of Responsibility en `ia.py`:** Se aisló el componente no determinista `AsistenteReglamento` detrás de `ProveedorLLM` y una cadena de guardrails deterministas (`SinIndicacionesDeVoto` y `SinResultadosInventados`) que bloquean cualquier sesgo electoral o alucinación de resultados antes de llegar al estudiante.

### Patrones rechazados
* **Abstract Factory:** Rechazado porque no existen familias de productos relacionados que deban crearse juntas; el registro simple en `FabricaFuentes` resuelve la creación con menor complejidad.
* **Singleton:** Rechazado tanto para `FabricaFuentes` como para `PublicadorEventos` porque introduce estado global mutable y dificulta la inyección de dobles de prueba independientes en `pytest`.

## Consecuencias
* **Positivas (+):**
  * La complejidad ciclomática de `emitir_voto()` se redujo de **18 (C)** a **4 (A)**, y la complejidad promedio del paquete bajó de **10.0 (B)** a **1.68 (A)**.
  * Se cumple el principio Abierto/Cerrado (OCP): es posible registrar nuevas fuentes de padrón, nuevos observadores de eventos o nuevos eslabones de guardrails sin editar `ServicioVotacion`.
  * Todo el sistema, incluido el asistente de IA, se ejecuta y verifica en menos de 0.15 segundos con dobles de prueba (`ClienteLLMFalso`), sin requerir conexión de red ni claves de API.
* **Negativas / Costos (-):**
  * El volumen de código fuente creció de **73 SLOC (1 archivo)** a **259 SLOC (6 archivos)** debido a las interfaces, adaptadores y clases de estado.
  * Aumenta el nivel de indirección, requiriendo que los integrantes del equipo conozcan la estructura de los patrones aplicados al dar mantenimiento.