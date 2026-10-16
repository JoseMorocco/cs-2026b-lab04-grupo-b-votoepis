# Inventario de elementos C4 — VotoEPIS

## 1. Descripción del sistema

VotoEPIS es una plataforma web para realizar elecciones digitales de delegados estudiantiles de la Escuela Profesional de Ingeniería de Sistemas. Permite gestionar el padrón electoral, verificar la habilitación de los estudiantes, registrar votos secretos, realizar el conteo y publicar los resultados y el acta electoral.

La arquitectura seleccionada en el Laboratorio 04 es un monolito en capas con PostgreSQL como base de datos.

## 2. Inventario de elementos

| Elemento | Tipo C4 | Descripción | Origen |
|---|---|---|---|
| Estudiante votante | Persona | Consulta su habilitación, emite su voto y revisa los resultados. | `docs/architecture/drivers.md` |
| Comité electoral | Persona | Gestiona el padrón, administra las elecciones y publica resultados y actas. | `docs/architecture/drivers.md` |
| Auditor | Persona | Verifica el proceso electoral y sus resultados. | `docs/architecture/drivers.md` |
| VotoEPIS | Sistema de software | Plataforma para realizar elecciones digitales de delegados estudiantiles. | `docs/architecture/adr/001-estilo-arquitectonico.md` |
| Servicio de correo institucional | Sistema externo | Envía notificaciones y confirmaciones a los estudiantes. | `docs/architecture/diagramas/arquitectura.mmd` |
| Sistema académico UNSA | Sistema externo propuesto | Fuente prevista para consultar datos de habilitación. | Guía del Laboratorio 06, tabla 10 |
| Aplicación web | Contenedor | Interfaz utilizada por estudiantes, comité electoral y auditor. | `docs/architecture/diagramas/arquitectura.mmd` |
| Aplicación VotoEPIS | Contenedor | Aplicación que implementa las reglas del proceso electoral. | `docs/architecture/adr/001-estilo-arquitectonico.md` |
| Base de datos | Contenedor | Almacena la información electoral en PostgreSQL. | `docs/architecture/adr/002-base-de-datos.md` |
| Acceso | Componente | Gestiona el acceso y la habilitación de los estudiantes. | `docs/design/paquetes.puml` |
| Padrón | Componente | Gestiona la información del padrón electoral. | `docs/design/paquetes.puml` |
| Votación | Componente | Valida y registra los votos. | `docs/design/paquetes.puml` |
| Auditoría | Componente | Registra eventos de seguridad y permite revisar el proceso electoral. | `docs/design/paquetes.puml` |
| Compartido | Componente de apoyo | Agrupa elementos utilizados por otros módulos. | `docs/design/paquetes.puml` |