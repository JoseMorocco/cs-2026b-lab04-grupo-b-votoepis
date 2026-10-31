workspace "VotoEPIS" "Modelo C4 de VotoEPIS refinado con ADD 3.0 para 25 000 votantes y auditoría externa (Lab 08)." {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante votante" "Consulta su habilitación, emite su voto único y revisa resultados [S1, S2, S6]."
        comite = person "Comité electoral" "Gestiona el padrón, administra el ciclo electoral y publica actas y huellas SHA-256 [S3, S4]."
        auditor = person "Auditor externo" "Recalcula totales y verifica la integridad del listado anónimo contra la huella SHA-256 externa [QA-03, S4, S5]."

        votoepis = softwareSystem "VotoEPIS" "Plataforma de elecciones universitarias (25 000 votantes / 8 h) con integridad transaccional y auditoría verificable [QA-01, QA-02, QA-03, QA-04]." {

            web = container "Aplicación web" "Interfaz de votación, panel electoral y portal de resultados y paquete de auditoría [QA-01, QA-03, S4, S6]." "Web" "Web Browser"

            app = container "Aplicación VotoEPIS" "Ejecuta reglas de habilitación extensible [QA-04, S7], emisión atómica [QA-01, QA-02, S1, S2] y generación de paquete auditable [QA-03, S4, S5, S8]." "Monolito en capas (Python 3.12)" {
                acceso = component "Acceso" "Gestiona la autenticación y el control de sesión de usuarios [QA-01]." "Módulo interno"
                padron = component "Padrón y Elegibilidad" "Verifica habilitación mediante PadronPort, FabricaFuentes y ConReintentos [QA-02, QA-04, S7]." "Módulo interno (Strategy/Adapter/Factory/Decorator)"
                votacion = component "Votación" "Coordina estado de elección y registro transaccional de participación y voto sin identidad [QA-01, QA-02, S1, S2, S5, S6]." "Módulo interno (State)"
                auditoria = component "Auditoría y Escrutinio" "Registra eventos INTENTO_DUPLICADO sin candidato_id y genera paquete de acta + listado anónimo con SHA-256 [QA-03, S4, S5, S8]." "Módulo interno (Observer)"
                compartido = component "Compartido y Dominio" "Entidades de dominio y puertos independientes de infraestructura, protegidos por FF-01 y FF-02 [QA-04, S7]." "Módulo interno"
            }

            db = container "Base de datos" "Almacena tablas separadas de participación con UNIQUE(estudiante_id, eleccion_id) y voto anónimo en transacción ACID [QA-01, QA-02, S1, S2, S5]." "PostgreSQL 16" {
                tags "Database"
            }
        }

        correo = softwareSystem "Servicio de correo institucional" "Envía confirmaciones de participación sin revelar candidato y distribuye copia externa de huella SHA-256 [QA-01, QA-03, S4, S5]." "Externo"
        academico = softwareSystem "Sistema académico UNSA" "Fuente externa de habilitación integrada mediante SistemaAcademicoAdapter y ConReintentos [QA-02, QA-04, S7]." "Externo"

        estudiante -> votoepis "Emite voto único y consulta resultados [S1, S6]"
        comite -> votoepis "Administra elección y publica paquete auditable [S3, S4]"
        auditor -> votoepis "Descarga acta y listado anónimo para verificar SHA-256 [S4, S5]"
        votoepis -> correo "Envía confirmaciones sin candidato y huella externa [S4, S5]"
        votoepis -> academico "Consulta condición de habilitación con reintentos [S7]"

        estudiante -> votoepis.web "Emite voto y consulta resultados [S1, S6]" "HTTPS"
        comite -> votoepis.web "Gestiona elección y cierre electoral [S3, S4]" "HTTPS"
        auditor -> votoepis.web "Verifica paquete de escrutinio y SHA-256 [S4, S5]" "HTTPS"
        votoepis.web -> votoepis.app "Solicita operaciones electorales (p95 <= 2 s) [S6]" "HTTPS"
        votoepis.app -> votoepis.db "Ejecuta transacción ACID participación (UNIQUE) + voto y consulta escrutinio [S1, S2, S4, S5]" "SQL / ACID"
        votoepis.app -> correo "Publica confirmación de participación y copia de huella [S4, S5]" "SMTP"
        votoepis.app -> academico "Consulta habilitación mediante PadronPort [S7]" "HTTPS"

        votoepis.web -> votoepis.app.acceso "Solicita autenticación [QA-01]" "HTTPS"
        votoepis.web -> votoepis.app.votacion "Solicita emisión de voto [S1, S2, S6]" "HTTPS"
        votoepis.web -> votoepis.app.padron "Consulta habilitación [S7]" "HTTPS"
        votoepis.web -> votoepis.app.auditoria "Consulta paquete de auditoría (acta + listado + SHA-256) [S4]" "HTTPS"

        votoepis.app.votacion -> votoepis.app.padron "Verifica habilitación electoral [S7]" "PadronPort"
        votoepis.app.votacion -> votoepis.app.auditoria "Publica eventos sin candidato_id [S5, S8]" "PublicadorEventos"
        votoepis.app.votacion -> votoepis.app.compartido "Usa entidades y puertos de dominio [FF-01]"
        votoepis.app.padron -> votoepis.app.compartido "Implementa PadronPort [FF-01, FF-02]"
        votoepis.app.auditoria -> votoepis.app.compartido "Usa contratos de dominio [FF-01, FF-02]"
        votoepis.app.acceso -> votoepis.app.compartido "Usa elementos comunes"

        votoepis.app.votacion -> votoepis.db "BEGIN / INSERT participacion [UNIQUE] + INSERT voto [anónimo] / COMMIT o ROLLBACK [S1, S2, S5]" "SQL"
        votoepis.app.padron -> votoepis.db "Consulta padrón local [S7]" "SQL"
        votoepis.app.padron -> academico "Adapta consulta académica con reintentos [S7]" "HTTPS"
        votoepis.app.auditoria -> votoepis.db "Registra INTENTO_DUPLICADO y exporta listado canónico [S4, S8]" "SQL"
        votoepis.app.auditoria -> correo "Envía confirmación sin candidato y huella SHA-256 [S4, S5]" "SMTP"

        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Dispositivo del usuario" "Cliente de votación y auditoría" "PC o Móvil (Navegador Web)" {
                containerInstance votoepis.web
            }
            deploymentNode "VPS Económico (R-04)" "Servidor único del MVP para 25 000 votantes [S3, S6]" "Ubuntu 24.04 LTS (2 vCPU, 4 GB RAM)" {
                deploymentNode "Docker Compose" "Orquestación local de contenedores" "Docker Engine 27 + Nginx" {
                    containerInstance votoepis.app
                    containerInstance votoepis.db
                }
            }
        }
    }

    views {
        systemContext votoepis "Contexto" "Nivel 1: VotoEPIS, actores y sistemas externos con trazabilidad QA/S." {
            include *
            autolayout lr
        }

        container votoepis "Contenedores" "Nivel 2: Contenedores de VotoEPIS después de 3 iteraciones de ADD [S1, S2, S4, S5, S6, S7]." {
            include *
            autolayout lr
        }

        component votoepis.app "Componentes" "Nivel 3: Componentes internos de Aplicación VotoEPIS y trazabilidad a escenarios." {
            include *
            autolayout lr
        }

        dynamic votoepis.app "EmitirVoto" "Vista dinámica: Emisión atómica y prevención de duplicados [S1, S2, S5, S8]." {
            votoepis.web -> votoepis.app.votacion "Solicita la emisión de voto"
            votoepis.app.votacion -> votoepis.app.padron "Verifica habilitación electoral (ConReintentos)"
            votoepis.app.padron -> votoepis.db "Consulta padrón"
            votoepis.app.votacion -> votoepis.db "Transacción ACID: INSERT participacion [UNIQUE] + INSERT voto [anónimo]"
            votoepis.app.votacion -> votoepis.app.auditoria "Publica evento sin candidato_id"
            votoepis.app.auditoria -> correo "Envía confirmación de participación"
            autolayout lr
        }

        deployment votoepis produccion "Despliegue" "Vista de despliegue en VPS único (R-04) [S3, S6]." {
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
            element "Web Browser" {
                shape WebBrowser
            }
            element "Externo" {
                background #999999
                color #ffffff
            }
        }
    }
}