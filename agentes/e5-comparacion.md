# E5 — Agente único vs actor-crítico (ISSUE-02)

## Variante A — agente único
- Traza: `agentes/trazas/issue-02-variante-a/traza.jsonl`, Mermaid `trayectoria.mmd`, diff `cambios.diff`.
- Pasos/decisiones: 6; acciones de herramienta: 5; rechazos por contrato: 0.
- Acciones bloqueadas por política: 0.
- Contexto final: 6796 caracteres (última solicitud).
- Resultado pytest: código 0.

## Variante B — actor-crítico
- Resumen: `agentes/trazas/issue-02-variante-b/resumen.json`, diff `cambios.diff`, pytest `pytest.txt`.
- Rondas: 1 de máximo 2; veredicto: APROBADO.
- Acciones de herramienta: 1 edición + 1 prueba + 1 diff (ejecutor único); revisor solo lectura.
- Contexto final: no aplica contexto LLM único; el ejecutor reutiliza la copia aislada.
- Resultado pytest: código 0.

## Conclusión
En VotoEPIS el defecto de ISSUE-02 es local y de una línea; un agente único lo resuelve en 6 pasos con 6796 caracteres de contexto final y sin rechazos. La variante actor-crítico añade una ronda de revisión, más componentes y más evidencia, pero no detectó un error omitido por el agente único porque la corrección era directa. Según el principio de parsimonia, el costo adicional de múltiples agentes no compensa para este tipo de corrección pequeña y bien delimitada. La coordinación actor-crítico se reserva para cambios con mayor riesgo o ambigüedad, manteniendo el revisor de solo lectura y el límite de dos rondas.
