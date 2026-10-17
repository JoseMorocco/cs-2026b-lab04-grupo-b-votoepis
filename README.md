# VotoEPIS - Laboratorio 04: Fundamentos de arquitectura de software
Construcción de Software EPIS-UNSA

## Integrantes
2026-B Grupo B
| Nombre | Rol en el laboratorio |
|---|---|
| Morocco Saico Jose Manuel | Analista de Drivers (E1) y Matriz (E2) |
| Luque Guevara Fernando Gerson | Redactor de ADRs (E4) y Diagramador Mermaid (E3) |
| Hilacondo Begazo Emanuel David | Diagramador PlantUML/Python (E5, E6) |

## Caso
VotoEPIS es un sistema para la elección digital de delegados estudiantiles de la EPIS. Permite gestionar el padrón, emitir votos y publicar resultados auditables. El atributo de calidad crítico es la **Seguridad e integridad (QA-01)**, el cual asegura que el sistema protege el voto, evita alteraciones y rechaza intentos duplicados.

## Arquitectura elegida
```mermaid
flowchart TB
    EST([Estudiante votante])
    COM([Comité electoral])
    AUD([Auditor])

    subgraph PRES["Capa de presentación (aplicación web)"]
        UI_VOTO["Interfaz de votación"]
        UI_ADMIN["Panel del comité electoral"]
        UI_PUB["Portal público de resultados y acta"]
    end

    subgraph LOG["Capa de lógica de negocio (un solo despliegue)"]
        AUTH["Módulo de acceso y habilitación<br/>RF-02"]
        PADRON["Módulo de padrón electoral<br/>RF-01"]
        VOTO["Módulo de votación<br/>RF-03"]
        CONTEO["Módulo de conteo automático<br/>RF-04"]
        RESUL["Módulo de resultados<br/>RF-05"]
        ACTA["Módulo de acta electoral<br/>RF-06"]
    end

    subgraph DATOS["Capa de datos"]
        DB[("PostgreSQL<br/>padrón, participación, votos,<br/>resultados y actas")]
    end

    SMTP[["Servicio de correo institucional<br/>(servicio externo)"]]

    EST -->|vota| UI_VOTO
    COM -->|administra| UI_ADMIN
    AUD -->|verifica| UI_PUB
    EST -->|consulta resultados| UI_PUB

    UI_VOTO --> AUTH
    UI_VOTO --> VOTO
    UI_ADMIN --> PADRON
    UI_ADMIN --> CONTEO
    UI_ADMIN --> ACTA
    UI_PUB --> RESUL
    UI_PUB --> ACTA

    VOTO -->|verifica habilitación| AUTH
    CONTEO -->|lee votos válidos| VOTO
    RESUL -->|usa totales| CONTEO
    ACTA -->|usa resultados| RESUL

    AUTH --> DB
    PADRON --> DB
    VOTO --> DB
    CONTEO --> DB
    RESUL --> DB
    ACTA --> DB

    AUTH -.->|envía código de acceso| SMTP
```

## Decisiones arquitectónicas
* [ADR-001: Estilo arquitectónico](docs/architecture/adr/001-estilo-arquitectonico.md)
* [ADR-002: Base de datos](docs/architecture/adr/002-base-de-datos.md)
* [ADR-003: Auditoría y seguridad](docs/architecture/adr/003-auditoria-seguridad.md)

## Reflexión sobre el uso de la IA
El uso de herramientas de IA demostró ser un recurso sumamente valioso para la fase de exploración.
Sin embargo, su uso exige un alto nivel de pensamiento crítico por parte del equipo para evitar sesgos.
La IA tiende a sugerir patrones de diseño avanzados que pueden introducir sobreingeniería en el MVP.
Si estas sugerencias se aceptan sin verificación, ponen en riesgo las restricciones reales del proyecto.
Por ello, la decisión final siempre debe recaer en el juicio humano apoyado en la matriz de decisión.

## Diseño UML (Lab 05)

### Diagrama de Máquina de Estados (Elección)
```mermaid
stateDiagram-v2
    [*] --> CONFIGURADA: crear()
    CONFIGURADA --> ABIERTA: abrir()
    ABIERTA --> CERRADA: cerrar()
    CERRADA --> ESCRUTADA: iniciarEscrutinio()
    ESCRUTADA --> PUBLICADA: publicarResultados()
    PUBLICADA --> [*]
```

### Enlaces a diagramas y documentación
*   [Diagrama de Clases (PlantUML)](docs/design/clases.puml)
*   [Diagrama de Secuencia - Emitir Voto (PlantUML)](docs/design/secuencia-emitir-voto.puml)
*   [Diagrama de Actividades - Escrutinio (PlantUML)](docs/design/actividades-escrutinio.puml)
*   [Diagrama de Paquetes (PlantUML)](docs/design/paquetes.puml)
*   [Ingeniería Round-Trip: Diagrama vs. Código](docs/design/round-trip.md)
*   [Auditoría de Consistencia (Reglas C1-C5)](docs/design/consistencia.md)
*   [Bitácora de IA (Lab 05)](docs/design/bitacora-ia.md)

## Arquitectura C4 (Lab 06)

### Diagrama de Contexto (Mermaid C4)
```mermaid
C4Context
    title System Context View: VotoEPIS

    Person(estudiante, "Estudiante votante", "Consulta su habilitación, emite su voto y revisa los resultados.")
    Person(comite, "Comité electoral", "Gestiona el padrón, administra las elecciones y publica resultados y actas.")
    Person(auditor, "Auditor", "Revisa los resultados y verifica el acta electoral.")

    System(votoepis, "VotoEPIS", "Plataforma para realizar elecciones estudiantiles y publicar resultados verificables.")

    System_Ext(correo, "Servicio de correo institucional", "Servicio externo de envío de correos y confirmaciones.")
    System_Ext(academico, "Sistema académico UNSA", "Posible fuente de información para verificar la habilitación de estudiantes; integración pendiente de confirmar.")

    Rel(estudiante, votoepis, "Consulta su habilitación, emite su voto y revisa resultados")
    Rel(comite, votoepis, "Gestiona el padrón y las elecciones; publica resultados y actas")
    Rel(auditor, votoepis, "Consulta el acta y verifica los resultados")
    Rel(votoepis, correo, "Envía confirmaciones y avisos por correo institucional")
    Rel(votoepis, academico, "Consulta datos de habilitación (integración propuesta)")
```

### Vistas Exportadas y Documentación C4
* [Inventario de Elementos C4](docs/architecture/c4/inventario.md)
* [Modelo Único en Structurizr DSL](docs/architecture/c4/workspace.dsl)
* **Imágenes de las 5 vistas C4:**
  * [Nivel 1: Diagrama de Contexto (PNG)](docs/architecture/c4/img/structurizr-Contexto.png)
  * [Nivel 2: Diagrama de Contenedores (PNG)](docs/architecture/c4/img/structurizr-Contenedores.png)
  * [Nivel 3: Diagrama de Componentes (PNG)](docs/architecture/c4/img/structurizr-Componentes.png)
  * [Vista Dinámica: Emitir Voto (PNG)](docs/architecture/c4/img/structurizr-EmitirVoto.png)
  * [Vista de Despliegue: Producción (PNG)](docs/architecture/c4/img/structurizr-Despliegue.png)
  * [Diagrama de Contexto Manual C4-PlantUML (PNG)](docs/architecture/c4/img/contexto-manual.png)
* [Comparación de Vistas y Herramientas (E4 y E6)](docs/architecture/c4/comparacion.md)
* [Revisión Oficial C4 y Auditoría IA (E7)](docs/architecture/c4/revision-c4.md)
* [Explicación para Público No Técnico (E7)](docs/architecture/c4/explicacion.md)
* [Bitácora de Uso de IA (Lab 06)](docs/architecture/c4/bitacora-ia.md)