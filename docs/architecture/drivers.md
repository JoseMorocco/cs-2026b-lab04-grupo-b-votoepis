# Drivers arquitectónicos - VotoEPIS

## 1. Requisitos funcionales clave
| ID | Requisito | Actor | Prioridad |
| :--- | :--- | :--- | :--- |
| RF-01 | Gestionar el padrón electoral. | Comité electoral | Alta |
| RF-02 | Verificar si un estudiante está habilitado para votar. | Estudiante | Alta |
| RF-03 | Registrar la emisión del voto evitando más de un voto por estudiante. | Estudiante | Alta |
| RF-04 | Realizar el conteo automático de los votos. | Sistema | Alta |
| RF-05 | Publicar los resultados de la elección. | Comité electoral | Alta |
| RF-06 | Generar y publicar el acta electoral. | Comité electoral | Media |

## 2. Atributos de calidad (ordenados por prioridad)
| ID | Atributo | Justificación / Descripción | Prioridad |
| :--- | :--- | :--- | :--- |
| QA-01 | Seguridad e integridad | El sistema debe proteger el voto y evitar alteraciones o duplicidad. | Crítica |
| QA-02 | Fiabilidad | El proceso electoral debe mantenerse disponible y conservar correctamente la información. | Alta |
| QA-03 | Auditabilidad | Los resultados deben poder ser comprobados de manera independiente. | Alta |
| QA-04 | Mantenibilidad | El sistema debe poder modificarse sin afectar todo el funcionamiento. | Media |

## 3. Restricciones
| ID | Tipo | Restricción |
| :--- | :--- | :--- |
| R-01 | Plazo | El MVP debe estar en producción en un plazo máximo de 1 mes. |
| R-02 | Equipo | El desarrollo estará a cargo de un equipo de máximo 3 integrantes. |
| R-03 | Tecnología | Se deben utilizar tecnologías que el equipo ya conozca. |
| R-04 | Presupuesto | El presupuesto disponible para el MVP es bajo y cualquier servicio de pago debe estar justificado. |

## 4. Escenarios de atributos de calidad
| ID | Atributo | Fuente | Estímulo | Entorno | Artefacto | Respuesta | Medida |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| QA-01 | Seguridad e integridad | Estudiante | Intenta emitir un segundo voto | Durante una elección activa | Módulo de votación | El sistema rechaza la segunda emisión | 100 % de los intentos duplicados rechazados |
| QA-02 | Fiabilidad | Estudiante | Envía un voto válido | Elección activa | Servicio de votación y BD | El voto queda registrado correctamente | 100 % de los votos válidos procesados durante las pruebas quedan registrados correctamente |
| QA-03 | Auditabilidad | Auditor | Solicita verificar los resultados | Elección finalizada | Módulo de resultados y acta | El sistema proporciona información verificable | 100 % de resultados publicados asociados a un acta |