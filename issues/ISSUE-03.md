# ISSUE-03 — La elección puede cerrarse antes de la hora programada

Defecto sembrado para el Lab 10 en agentes/demo/cierre.py. La máquina histórica permite cerrar una elección abierta sin horario. La demostración introduce un instante de cierre con zona horaria y establece que cerrar es válido desde ese instante inclusive.

## Observado y esperado

La comparación usa solo la fecha y permite cerrar un segundo antes de las 18 horas del mismo día. El contrato local exige rechazar ese instante y aceptar exactamente el cierre programado.

## Reproducción y prueba

Configurar cierre a las 18 horas del 21 de noviembre de 2026 con desplazamiento UTC-5 y consultar un segundo antes:

```powershell
python -m pytest --runxfail -q tests/test_issue_03.py
```

test_issue_03_respeta_instante_de_cierre falla porque puede_cerrar devuelve True para el segundo anterior. El xfail estricto conserva el defecto pendiente en CI.

## Resolución objetiva y archivos

La prueba debe pasar con --runxfail sin cambiar sus dos aserciones. Archivos implicados agentes/demo/cierre.py y tests/test_issue_03.py. Esta regla horaria pertenece a la demostración y requiere revisión de negocio antes de incorporarse al producto. El issue mantiene su xfail durante E2.
