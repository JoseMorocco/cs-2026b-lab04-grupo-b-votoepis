# ISSUE-01 — Código con mayúsculas permite repetir la participación

Defecto sembrado para el Lab 10 en agentes/demo/codigos.py. El servicio histórico usa UUID. Esta demostración introduce un registro por código en memoria para estudiar la unicidad por elección de RF-03 y HU-01.

## Observado y esperado

La clave incluye el código literal. epis42 y EPIS42 se aceptan para una misma elección. El contrato de la demostración define esos códigos como la misma persona, por lo que la segunda emisión debe rechazarse. La participación en una elección distinta se permite.

## Reproducción y prueba

Crear RegistroPorCodigo, emitir para eleccion-A con epis42 y repetir con EPIS42. Ejecutar desde la raíz:

```powershell
python -m pytest --runxfail -q tests/test_issue_01.py
```

La prueba test_issue_01_impide_doble_voto_por_cambio_de_mayusculas falla al comprobar que la segunda emisión sea False. Su xfail estricto documenta el defecto pendiente en CI.

## Resolución objetiva y archivos

La prueba debe pasar con --runxfail, conservar una participación en eleccion-A y permitir votar en eleccion-B. El agente puede corregir agentes/demo/codigos.py en su copia temporal. tests/test_issue_01.py queda protegido. Una vez acreditada la corrección real de E2, un humano retira únicamente el marcador xfail de esta prueba.
