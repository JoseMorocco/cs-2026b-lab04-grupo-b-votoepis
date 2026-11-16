# Product Backlog de VotoEPIS para el Laboratorio 09

HU-01 es la historia existente y conserva su identificador y redacción de origen. HU-L09-02 a HU-L09-06 son propuestas para revisión del equipo, derivadas de los requisitos funcionales versionados. El estado de cada entrada se refiere a su revisión para el Laboratorio 09.

## HU-01 — Emitir un voto secreto

**Estado** — Borrador — pendiente de revisión del equipo

**Historia existente** — Como estudiante votante habilitado, quiero emitir mi voto de forma secreta en una elección abierta, para elegir a los representantes estudiantiles garantizando que mi identidad no quede vinculada a mi candidato y que solo pueda votar una vez.

**Origen** — [Historia original HU-01](design/historia.md) y [RF-03, registrar la emisión del voto evitando duplicados](architecture/drivers.md#1-requisitos-funcionales-clave).

**Reglas documentadas**

- El estudiante debe estar habilitado, la elección debe estar abierta y el candidato debe pertenecer a esa elección. La participación queda registrada sin vincular la identidad del estudiante con su preferencia. La historia prevé una confirmación asíncrona por correo institucional. [HU-01, historia y criterios](design/historia.md#criterios-de-aceptación)
- Un intento repetido en la misma elección se rechaza, queda registrado como evento de seguridad y no suma otro voto. [HU-01, criterios](design/historia.md#criterios-de-aceptación)

**Preguntas para el equipo**

- ¿La confirmación asíncrona sigue siendo la regla de producto? La historia la especifica y el prototipo documenta un envío síncrono. [Escenarios de calidad, base arquitectónica y alcance](architecture/utilidad/escenarios.md#base-arquitectónica-y-alcance)

## HU-L09-02 — Gestionar el padrón electoral

**Estado** — Borrador — pendiente de revisión del equipo

**Historia propuesta** — Como integrante del comité electoral, quiero gestionar el padrón de una elección, para que el proceso electoral disponga de la información con la que se verifica quién puede votar.

**Origen** — [RF-01, gestionar el padrón electoral](architecture/drivers.md#1-requisitos-funcionales-clave).

**Reglas documentadas**

- El comité electoral gestiona el padrón. [Drivers arquitectónicos, RF-01](architecture/drivers.md#1-requisitos-funcionales-clave)
- Para abrir una elección, el padrón debe estar cargado y debe haber candidatos registrados. [Diagrama de estados de la elección](design/estados-eleccion.mmd#L4)

**Preguntas para el equipo**

- ¿Qué operaciones de gestión del padrón están dentro del alcance y quién puede realizarlas?
- ¿Qué regla debe aplicar el comité ante registros duplicados o solicitudes de corrección? ¿En qué estados de la elección se permiten cambios?

## HU-L09-03 — Consultar la habilitación para votar

**Estado** — Borrador — pendiente de revisión del equipo

**Historia propuesta** — Como estudiante, quiero consultar si estoy habilitado para votar en una elección, para saber si puedo participar.

**Origen** — [RF-02, verificar si un estudiante está habilitado para votar](architecture/drivers.md#1-requisitos-funcionales-clave).

**Reglas documentadas**

- El estudiante puede consultar su habilitación y el módulo de votación la verifica antes de registrar una emisión. [Vista de contexto](../README.md#diagrama-de-contexto-mermaid-c4) · [Servicio de votación](../src/votacion/servicio.py#L99)
- La comprobación se refiere a un estudiante y una elección concretos. [Contrato de consulta de habilitación](design/clases.puml#L46)

**Preguntas para el equipo**

- ¿Qué condiciones determinan la habilitación y qué fuente prevalece si el padrón local y el sistema académico discrepan?
- ¿Qué debe distinguir la consulta entre un estudiante que no está habilitado y una verificación que no pudo realizarse?

## HU-L09-04 — Contar automáticamente los votos

**Estado** — Borrador — pendiente de revisión del equipo

**Historia propuesta** — Como integrante del comité electoral, quiero que el sistema cuente automáticamente los votos por candidato, para disponer de los totales y comprobar que coinciden con la participación registrada.

**Origen** — [RF-04, realizar el conteo automático de los votos](architecture/drivers.md#1-requisitos-funcionales-clave). RF-04 asigna el conteo al sistema. El comité es el actor de la historia porque solicita el escrutinio en el flujo documentado. [Diagrama de actividades del escrutinio](design/actividades-escrutinio.puml#L4)

**Reglas documentadas**

- Un comité autorizado puede iniciar el escrutinio cuando la elección está cerrada. [Diagrama de estados de la elección](design/estados-eleccion.mmd#L6)
- El sistema cuenta los votos por candidato y compara el total de votos con el total de participaciones registradas. Si existe una discrepancia, se registra un evento de seguridad y el auditor la investiga. [Diagrama de actividades del escrutinio](design/actividades-escrutinio.puml#L18)

**Preguntas para el equipo**

- ¿Quién puede autorizar la reanudación del escrutinio después de investigar una discrepancia y bajo qué condiciones?
- ¿Qué tratamiento requiere una elección cerrada sin votos?

## HU-L09-05 — Publicar los resultados electorales

**Estado** — Borrador — pendiente de revisión del equipo

**Historia propuesta** — Como integrante del comité electoral, quiero publicar los resultados de la elección una vez verificados, para que los estudiantes puedan consultarlos y el auditor pueda comprobarlos.

**Origen** — [RF-05, publicar los resultados de la elección](architecture/drivers.md#1-requisitos-funcionales-clave).

**Reglas documentadas**

- La elección pasa de escrutada a publicada con acta firmada y totales verificados. [Diagrama de estados de la elección](design/estados-eleccion.mmd#L7)
- Cada resultado publicado debe quedar asociado a un acta para permitir la verificación independiente. [Escenario QA-03](architecture/drivers.md#4-escenarios-de-atributos-de-calidad) · [ADR-003](architecture/adr/003-auditoria-seguridad.md#decisión)

**Preguntas para el equipo**

- ¿Quién da la autorización final de publicación después de la verificación del auditor?
- ¿Cómo se procede si se descubre un error en resultados ya publicados?

## HU-L09-06 — Generar y publicar el acta electoral

**Estado** — Borrador — pendiente de revisión del equipo

**Historia propuesta** — Como integrante del comité electoral, quiero revisar, firmar y publicar el acta generada con los resultados del escrutinio, para que un auditor pueda verificar el conteo de forma independiente.

**Origen** — [RF-06, generar y publicar el acta electoral](architecture/drivers.md#1-requisitos-funcionales-clave).

**Reglas documentadas**

- Cuando coinciden los totales de votos y de participación, el sistema genera el acta. El comité la revisa y firma, el auditor verifica el acta y los resultados, y el sistema publica el acta firmada. [Diagrama de actividades del escrutinio](design/actividades-escrutinio.puml#L24)
- El acta documenta los totales por candidato, la fecha de cierre y la huella SHA-256 del listado anonimizado. El listado acompaña al acta y la huella se publica también en un canal independiente para permitir el contraste. [ADR-003](architecture/adr/003-auditoria-seguridad.md#decisión) · [ADR-008](architecture/adr/008-paquete-verificable-auditoria-externa.md#decisión)

**Preguntas para el equipo**

- ¿Quiénes deben firmar el acta y qué forma de firma se considera válida?
- ¿Qué canal independiente se usará para publicar la huella y quién será responsable de esa publicación? [ADR-008, estado](architecture/adr/008-paquete-verificable-auditoria-externa.md#L4)
