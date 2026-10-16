workspace "VotoEPIS" "Modelo C4 de la plataforma de elecciones digitales de delegados estudiantiles de EPIS." {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante votante" "Consulta su habilitación, emite su voto y revisa los resultados."

        comite = person "Comité electoral" "Gestiona el padrón, administra las elecciones y publica resultados y actas."

        auditor = person "Auditor" "Revisa los resultados y verifica el acta electoral."

        votoepis = softwareSystem "VotoEPIS" "Plataforma para realizar elecciones estudiantiles y publicar resultados verificables." {

            web = container "Aplicación web" "Presenta la interfaz de votación, el panel electoral y la consulta pública de resultados." "Web"

            app = container "Aplicación VotoEPIS" "Implementa las reglas de acceso, padrón, votación, conteo, resultados y actas." "Monolito en capas"

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
