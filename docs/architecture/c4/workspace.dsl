workspace "VotoEPIS" "Modelo C4 de la plataforma de elecciones digitales de delegados estudiantiles de EPIS." {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante votante" "Consulta su habilitación, emite su voto y revisa los resultados."

        comite = person "Comité electoral" "Gestiona el padrón, administra las elecciones y publica resultados y actas."

        auditor = person "Auditor" "Revisa los resultados y verifica el acta electoral."

        votoepis = softwareSystem "VotoEPIS" "Plataforma para realizar elecciones estudiantiles y publicar resultados verificables." {

            web = container "Aplicación web" "Presenta la interfaz de votación, el panel electoral y la consulta pública de resultados." "Web"

            app = container "Aplicación VotoEPIS" "Implementa las reglas de acceso, padrón, votación, conteo, resultados y actas." "Monolito en capas" {

                acceso = component "Acceso" "Gestiona el acceso de los usuarios al sistema electoral." "Módulo interno"

                padron = component "Padrón" "Consulta el padrón y verifica la habilitación de los estudiantes." "Módulo interno"

                votacion = component "Votación" "Valida las condiciones de emisión y registra los votos." "Módulo interno"

                auditoria = component "Auditoría" "Registra eventos de seguridad y operaciones relevantes del proceso electoral." "Módulo interno"

                compartido = component "Compartido" "Proporciona elementos comunes utilizados por los otros módulos." "Módulo interno"
            }

            db = container "Base de datos" "Almacena padrón, participaciones, votos, resultados, actas y registros de auditoría." "PostgreSQL" {
                tags "Database"
            }
        }

        correo = softwareSystem "Servicio de correo institucional" "Servicio externo de envío de correos y confirmaciones." "Externo"

        academico = softwareSystem "Sistema académico UNSA" "Posible fuente de información para verificar la habilitación de estudiantes; integración pendiente de confirmar." "Externo"

        // Relaciones del contexto (E1)

        estudiante -> votoepis "Consulta su habilitación, emite su voto y revisa resultados"

        comite -> votoepis "Gestiona el padrón y las elecciones; publica resultados y actas"

        auditor -> votoepis "Consulta el acta y verifica los resultados"

        votoepis -> correo "Envía confirmaciones y avisos por correo institucional"

        votoepis -> academico "Consulta datos de habilitación (integración propuesta)"

        // Relaciones entre contenedores (E2)

        estudiante -> votoepis.web "Emite votos y consulta resultados" "HTTPS"

        comite -> votoepis.web "Administra elecciones y publica actas" "HTTPS"

        auditor -> votoepis.web "Consulta resultados y actas" "HTTPS"

        votoepis.web -> votoepis.app "Solicita operaciones electorales" "HTTPS"

        votoepis.app -> votoepis.db "Consulta y registra información electoral" "SQL"

        votoepis.app -> correo "Solicita el envío de correos institucionales" "SMTP"

        votoepis.app -> academico "Consulta información de habilitación (propuesta)" "Integración por definir"

        // Relaciones de componentes (E3)

        votoepis.web -> votoepis.app.acceso "Solicita operaciones de acceso" "HTTPS"

        votoepis.web -> votoepis.app.votacion "Solicita la emisión de votos" "HTTPS"

        votoepis.web -> votoepis.app.padron "Solicita consultas y gestión del padrón" "HTTPS"

        votoepis.web -> votoepis.app.auditoria "Solicita consultas de auditoría" "HTTPS"

        // Dependencias de los paquetes UML

        votoepis.app.votacion -> votoepis.app.padron "Verifica la habilitación electoral" "PadronPort"

        votoepis.app.votacion -> votoepis.app.auditoria "Registra intentos duplicados"

        votoepis.app.votacion -> votoepis.app.compartido "Utiliza elementos comunes"

        votoepis.app.padron -> votoepis.app.compartido "Utiliza elementos comunes"

        votoepis.app.auditoria -> votoepis.app.compartido "Utiliza elementos comunes"

        votoepis.app.acceso -> votoepis.app.compartido "Utiliza elementos comunes"

        // Persistencia

        votoepis.app.votacion -> votoepis.db "Registra votos y participaciones" "SQL"

        votoepis.app.padron -> votoepis.db "Consulta información del padrón" "SQL"

        votoepis.app.auditoria -> votoepis.db "Registra eventos de seguridad" "SQL"
    }

    views {
        systemContext votoepis "Contexto" "Nivel 1: VotoEPIS, sus usuarios y sistemas externos." {
            include *
            autolayout lr
        }

        container votoepis "Contenedores" "Nivel 2: contenedores lógicos de VotoEPIS y sus relaciones." {
            include *
            autolayout lr
        }

        component votoepis.app "Componentes" "Nivel 3: componentes internos de la Aplicación VotoEPIS y sus dependencias." {
            include *
            autolayout lr
        }

        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }

            element "Software System" {
                background #1168BD
                color #ffffff
            }

            element "Container" {
                background #438DD5
                color #ffffff
            }

            element "Component" {
                background #85BBF0
                color #000000
            }

            element "Database" {
                shape cylinder
            }

            element "Externo" {
                background #999999
                color #ffffff
            }
        }
    }
}
