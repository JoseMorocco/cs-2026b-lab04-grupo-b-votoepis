# ISSUE-02 — El voto en blanco incrementa los votos válidos

Defecto sembrado para el Lab 10 en agentes/demo/conteo.py. RF-04 documenta conteo automático, pero el prototipo histórico exige un candidato de la elección. La demostración incorpora None como blanco y define válidos como votos con candidato, separados de blancos. Esta convención debe revisarse si se incorpora al producto.

## Observado y esperado

Para candidato-A, None y candidato-B, contar devuelve tres válidos y un blanco. El contrato local espera dos válidos y un blanco.

## Reproducción y prueba

Invocar contar(["candidato-A", None, "candidato-B"]) y comparar el resultado completo:

```powershell
python -m pytest --runxfail -q tests/test_issue_02.py
```

test_issue_02_separa_blancos_de_validos falla por la diferencia en validos, de 3 frente a 2. El xfail estricto conserva esa expectativa funcional en CI.

## Resolución objetiva y archivos

La prueba debe pasar con --runxfail conservando la aserción. Archivos implicados agentes/demo/conteo.py y tests/test_issue_02.py. Este issue permanece pendiente durante E2 y mantiene su xfail.
