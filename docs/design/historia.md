# HU-01: Emitir un voto secreto

**Como** estudiante votante habilitado,  
**quiero** emitir mi voto de forma secreta en una elección abierta,  
**para** elegir a los representantes estudiantiles garantizando que mi identidad no quede vinculada a mi candidato y que solo pueda votar una vez.

## Criterios de aceptación

1. **Voto exitoso y anónimo:**  
   Dado un estudiante habilitado que aún no tiene participación registrada en la elección,  
   cuando selecciona un candidato de esa elección y confirma su voto,  
   entonces el sistema registra la participación y el voto en tablas separadas dentro de una transacción, y envía asíncronamente un correo institucional de confirmación.

2. **Rechazo por voto duplicado:**  
   Dado un estudiante que ya tiene participación registrada en la elección,  
   cuando intenta votar nuevamente,  
   entonces el sistema rechaza la solicitud, no registra un segundo voto y registra el intento en los eventos de seguridad, conforme al ADR-003.
