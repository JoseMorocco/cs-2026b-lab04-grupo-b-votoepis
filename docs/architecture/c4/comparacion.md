# Comparación de Vistas y Herramientas — VotoEPIS (Lab 06)

## 1. Vista Dinámica C4 vs. Diagrama de Secuencia UML (E4)
La secuencia UML muestra métodos con parámetros (emitirVoto(estudianteId, eleccionId, candidatoId)), fragmentos alt/opt, creación de objetos (Participacion, Voto, EventoSeguridad), retornos y el límite transaccional. La vista dinámica C4 omite todo eso y resume la colaboración en cinco pasos entre contenedores y componentes. La secuencia sirve a los desarrolladores que implementan el código. La vista dinámica sirve a arquitectos y líderes técnicos que validan el flujo sin detalles de implementación.

## 2. Modelado (Structurizr DSL) vs. Diagramación Manual (C4-PlantUML) (E6)

| Criterio | Escritura a mano (`contexto-manual.puml`) | Modelo único exportado (`workspace.dsl`) |
|---|---|---|
| **Tiempo invertido** | Rápido para un único diagrama aislado, pero lento y repetitivo al construir las 5 vistas porque obliga a redeclarar elementos manualmente en cada archivo. | Requiere mayor inversión inicial para estructurar el DSL, pero genera las 5 vistas en segundos de forma automatizada mediante `structurizr export`. |
| **Errores encontrados** | Propenso a errores de tipeo en las macros (`Person`, `System_Ext`, `Rel`), omisión de leyendas (`SHOW_LEGEND()`) e inconsistencias en los nombres o descripciones entre distintos archivos `.puml`. | El validador (`structurizr validate`) detecta inmediatamente referencias inexistentes, relaciones hacia identificadores no declarados y errores sintácticos antes de exportar. |
| **Impacto si mañana cambia el nombre de un contenedor** | **Alto riesgo de desincronización:** Habría que buscar y editar manualmente el nombre en los archivos de Contenedores, Componentes, Vista Dinámica y Despliegue, aumentando el riesgo de dejar vistas desactualizadas. | **Mantenimiento centralizado:** Solo se modifica el nombre una única vez en la definición del contenedor dentro de `workspace.dsl` y, al reexportar, todas las vistas se actualizan automáticamente manteniendo coherencia total. |
