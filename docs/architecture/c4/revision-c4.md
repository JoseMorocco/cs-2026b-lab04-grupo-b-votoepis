# Revisión del Modelo C4 — VotoEPIS

## 1. Aplicación de la Lista de Revisión Oficial (c4model.com)

| Grupo | Pregunta de revisión | Contexto | Contenedores | Componentes | Dinámica | Despliegue | Evidencia / Observación |
|---|---|---|---|---|---|---|---|
| **General** | ¿Tiene título claro que indique el tipo de diagrama y alcance? | Sí | Sí | Sí | Sí | Sí | Todas las vistas incluyen encabezado generado por Structurizr (`System Context View`, `Container View`, etc.). |
| **General** | ¿Tiene leyenda que explique formas, colores y bordes? | Sí | Sí | Sí | Sí | Sí | El bloque `styles` y la exportación a C4-PlantUML incluyen `SHOW_LEGEND()` en los 5 diagramas. |
| **Elementos** | ¿Cada elemento tiene nombre, tipo C4 y descripción? | Sí | Sí | Sí | Sí | Sí | Todos los elementos declaran explícitamente nombre, estereotipo y responsabilidad en `workspace.dsl`. |
| **Elementos** | ¿Los contenedores, componentes y nodos indican su tecnología? | N/A | Sí | Sí | Sí | Sí | Se especifica `Web`, `Monolito en capas`, `PostgreSQL 16`, `Ubuntu 24.04 LTS` y `Docker Engine 27 + Nginx`. |
| **Relaciones** | ¿Cada flecha tiene una etiqueta con un verbo que describe su intención? | Sí | Sí | Sí | Sí | Sí | Se usan verbos precisos ("Verifica la habilitación electoral", "Registra votos y participaciones") evitando frases vagas como "usa". |
| **Relaciones** | ¿Se indica el protocolo o tecnología en las relaciones técnicas? | N/A | Sí | Sí | Sí | Sí | Las relaciones entre contenedores y componentes indican `HTTPS`, `SQL`, `SMTP` y `PadronPort`. |

## 2. Hallazgos del Segundo Revisor (Auditoría con IA - Prompt IA 2)

| Vista | Hallazgo reportado por la IA | Verificación del equipo |
|---|---|---|
| **Contexto** | La IA señaló como error que las relaciones entre los actores (`Estudiante votante`, `Comité electoral`, `Auditor`) y el sistema `VotoEPIS` no especifican el protocolo técnico (`HTTPS`). | **Falso positivo:** En el Nivel 1 (Contexto del sistema), el público objetivo incluye a personas no técnicas, por lo que no se exigen protocolos ni tecnologías en las interacciones de usuario. Se rechaza el hallazgo. |
| **Componentes** | La relación `votoepis.app.votacion -> votoepis.app.auditoria` ("Registra intentos duplicados") no especifica el mecanismo técnico de invocación. | **Correcto:** Al ser módulos dentro del mismo monolito en capas, la comunicación ocurre mediante llamadas directas en memoria (interfaz interna), lo cual es coherente con el ADR-001. |
| **Despliegue** | El contenedor `Base de datos` debe especificar la versión del motor en el nodo de ejecución. | **Correcto:** Se actualizó la tecnología del contenedor a `PostgreSQL 16` en `workspace.dsl` y se verificó su visualización en el diagrama exportado. |
| **Todas** | Todas las vistas cuentan con título, descripción de alcance, leyenda y dirección de flechas coherente. | **Correcto (cumple):** Verificado visualmente en los archivos PNG exportados. |