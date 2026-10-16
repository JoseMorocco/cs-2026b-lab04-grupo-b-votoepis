workspace "VotoEPIS" "Modelo C4 de la plataforma de elecciones digitales de delegados estudiantiles de EPIS." {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante votante" "Consulta su habilitación, emite su voto y revisa los resultados."

        comite = person "Comité electoral" "Gestiona el padrón, administra las elecciones y publica resultados y actas."

        auditor = person "Auditor" "Revisa los resultados y verifica el acta electoral."

        votoepis = softwareSystem "VotoEPIS" "Plataforma para realizar elecciones estudiantiles y publicar resultados verificables."

        correo = softwareSystem "Servicio de correo institucional" "Servicio externo de envío de correos y confirmaciones." "Externo"

        academico = softwareSystem "Sistema académico UNSA" "Posible fuente de información para verificar la habilitación de estudiantes; integración pendiente de confirmar." "Externo"

        estudiante -> votoepis "Consulta su habilitación, emite su voto y revisa resultados"

        comite -> votoepis "Gestiona el padrón y las elecciones; publica resultados y actas"

        auditor -> votoepis "Consulta el acta y verifica los resultados"

        votoepis -> correo "Envía confirmaciones y avisos por correo institucional"

        votoepis -> academico "Consulta datos de habilitación (integración propuesta)"
    }

    views {
        systemContext votoepis "Contexto" "Nivel 1: VotoEPIS, sus usuarios y sistemas externos." {
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

            element "Externo" {
                background #999999
                color #ffffff
            }
        }
    }
}
