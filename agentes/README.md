# Laboratorio 10 — Sistemas agénticos VotoEPIS

Este directorio contiene la implementación y las evidencias
del sistema agéntico desarrollado para VotoEPIS.

## Estructura

- diseno/: lienzo y máquina de estados.
- agente/: núcleo ReAct, contrato, herramientas y políticas.
- pruebas_agente/: pruebas del agente.
- trayectorias/: decisiones originales del modelo.
- trazas/: eventos JSONL y diagramas generados.

Los issues se encuentran en la carpeta issues/ del repositorio.

## Reglas de seguridad

- El agente actúa únicamente sobre una copia o rama de trabajo.
- Las decisiones se validan antes de ejecutar herramientas.
- Las acciones se restringen por política y permisos mínimos.
- El agente no modifica pruebas para hacerlas pasar.
- La aprobación y fusión de cambios corresponde a un humano.
