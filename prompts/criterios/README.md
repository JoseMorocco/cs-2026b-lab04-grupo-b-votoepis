# Línea base de criterios de aceptación

El dataset contiene una historia original, cinco propuestas derivadas aún pendientes de revisión y tres casos difíciles. Las expectativas están en `casos.yaml` y forman parte del commit de E1.

## Captura de respuestas v1

Desde la raíz del repositorio, prepara el entorno de pruebas y captura en PowerShell:

```powershell
python -m venv .venv
$python = (Resolve-Path .\.venv\Scripts\python.exe).Path
& $python -m pip install -r fitness/requirements.txt -r prompts/criterios/requirements.txt
& $python -m pytest -q tests prompts/criterios
```

Extrae el prompt completo para cada caso con el mismo identificador que aparece en `casos.yaml`. El comando puede escribir directamente en un archivo UTF-8:

```powershell
$id = 'HU-01'
$entrada = Join-Path $env:TEMP "votoepis-$id-prompt.txt"
$respuesta = Join-Path $env:TEMP "votoepis-$id-respuesta.txt"
& $python -m prompts.criterios.gestionar_grabaciones prompt $id --salida $entrada
Set-Clipboard -Value (Get-Content -LiteralPath $entrada -Encoding UTF8 -Raw)
```

Envía el contenido en una conversación nueva, sin añadir instrucciones ni adjuntar el esquema. Guarda la respuesta completa en UTF-8 en `$respuesta`. Conserva los bloques Markdown, comentarios y demás texto que el asistente haya devuelto. Registra cada respuesta con el nombre real del asistente y, si se conoce, el modelo que reportó.

```powershell
$asistente = Read-Host 'Asistente usado'
$modelo = Read-Host 'Modelo reportado, o Enter si no se pudo verificar'
if ($modelo) {
    & $python -m prompts.criterios.gestionar_grabaciones registrar $id $respuesta --asistente $asistente --modelo $modelo
} else {
    & $python -m prompts.criterios.gestionar_grabaciones registrar $id $respuesta --asistente $asistente
}
```

El manifiesto de procedencia vincula la versión, el caso, el asistente, la huella del prompt y la huella de los bytes de la respuesta. La huella del prompt normaliza únicamente los saltos CRLF a LF para permitir la reproducción en distintos sistemas. El proveedor devuelve la respuesta UTF-8 sin modificar sus saltos ni espacios.

La carga directa de `v1.txt` en promptfoo 0.125.1 descartaba el LF final conservado en la captura. En los nueve casos ese era el único cambio. Ahora la captura manual y el prompt dinámico usan `renderizar_prompt.py`, incluida la última línea. La configuración desactiva el procesamiento posterior de plantillas para conservar el texto renderizado.

| Caso | Caracteres y bytes UTF-8 de captura / evaluación anterior | SHA-256 de captura | SHA-256 de evaluación anterior |
| --- | --- | --- | --- |
| HU-01 | 891 y 903 / 890 y 902 | `8abfcf769ff8f9947c5991f569fe1835e40b48e98ddf1d8187144968c1a8c9b7` | `66a23cbabaab1f2750992bfdd6a1371dc3abfa153fbcb7d3543e66b01ba08f86` |
| LAB09-ADV | 869 y 878 / 868 y 877 | `eedfd2b0812079f4f2cb3b602f0ed43267816dbe4550cf847db48bea054982f8` | `d358779c47b1138cbb78ae78d0f6aff5a8dfcc53abc32f90e53b3731e43129fe` |

## Evaluación reproducible

Ejecuta la evaluación cuando la verificación confirme las nueve grabaciones:

```powershell
& $python -m prompts.criterios.gestionar_grabaciones verificar
if ($LASTEXITCODE -ne 0) { throw 'La captura v1 está incompleta o no coincide con su procedencia.' }
$env:PROMPTFOO_PYTHON = $python
$env:PROMPTFOO_DISABLE_TELEMETRY = '1'
$env:PROMPTFOO_DISABLE_UPDATE = '1'
npx.cmd --yes promptfoo@0.125.1 --version
npx.cmd --yes promptfoo@0.125.1 eval --no-cache --no-share -c prompts/criterios/promptfooconfig.yaml -o prompts/criterios/resultado-v1.json
```

La instalación inicial del CLI requiere acceso a npm. La evaluación usa el proveedor grabado y las aserciones deterministas locales. A1 comprueba el esquema y el identificador. A2 comprueba la cobertura de éxito y error o borde. A3 busca vocabulario de implementación solo en los escenarios. A4 comprueba el rechazo de historias no INVEST y usa la forma y longitud mínima de una pregunta como aproximación a su concreción. A5 comprueba la ausencia del marcador de inyección y que se conserve el identificador.

La revisión humana debe contrastar la pertinencia de las preguntas y la fidelidad de los escenarios con las reglas documentadas. El caso adversario comprueba una instrucción específica.

## Resultado v1

Promptfoo 0.125.1 evaluó las nueve respuestas obtenidas manualmente de ChatGPT. El modelo exacto figura como no verificado en el manifiesto. La tasa fue **88,89 %** con 8 casos aprobados, 1 fallido y 0 errores de evaluación. En HU-L09-06, ChatGPT marcó `invest_ok: false`, formuló preguntas sobre el alcance y la firma del acta y dejó `escenarios` vacío. A2 falló porque el caso esperaba al menos un escenario de éxito y uno de error o borde.

El [reporte JSON](resultado-v1.json) conserva los prompts evaluados, las respuestas literales y los resultados por aserción. Las rutas locales de configuración del reporte se guardaron como rutas relativas. Las huellas de los nueve prompts y de las nueve respuestas coinciden con el [manifiesto de captura](grabaciones/v1/procedencia.json).
