#!/usr/bin/env bash
set -euo pipefail

raiz=prompts/reto-opcional-a
a="$raiz/resultados/20261117T051313Z"
cfg="$raiz/promptfooconfig-b.yaml"
export PROMPTFOO_PYTHON="${PROMPTFOO_PYTHON:-$HOME/.venvs/votoepis-lab09/bin/python}"
export PROMPTFOO_DISABLE_TELEMETRY=1 PROMPTFOO_DISABLE_UPDATE=1
export OLLAMA_BASE_URL=http://127.0.0.1:11434 REQUEST_TIMEOUT_MS=180000
unset OLLAMA_API_KEY
cli=(npx --offline --yes promptfoo@0.125.1)
eval_args=(eval -c "$cfg" --no-cache --no-share --no-table --max-concurrency 1)
test "$(curl -fsS "$OLLAMA_BASE_URL/api/version" | "$PROMPTFOO_PYTHON" -c 'import json,sys; print(json.load(sys.stdin)["version"])')" = 0.40.16
test "$("${cli[@]}" --version)" = 0.125.1
grep -E '  prompts/(criterios/|reto-opcional-a/promptfooconfig.yaml)' "$a/entorno.txt" | sha256sum -c -

if [[ $# -eq 0 ]]; then
    salida="$raiz/resultados/B-$(date -u +%Y%m%dT%H%M%SZ)"
    mkdir "$salida"
    cp "$cfg" "$salida/configuracion.yaml"
    curl -fsS "$OLLAMA_BASE_URL/api/tags" > "$salida/modelos-ollama.json"
else
    test "$#" -eq 1
    salida="$1"
    [[ "$salida" =~ ^prompts/reto-opcional-a/resultados/B-[0-9]{8}T[0-9]{6}Z$ ]]
    cmp "$cfg" "$salida/configuracion.yaml"
fi
echo "DIRECTORIO=$salida"
test ! -e "$salida/promptfoo.json"
test ! -e "$salida/evaluacion.log"
"$PROMPTFOO_PYTHON" - "$a/modelos-ollama.json" "$salida/modelos-ollama.json" <<'PY'
import json, sys
from pathlib import Path

def inventario(archivo):
    return {m["name"]: m["digest"] for m in json.loads(Path(archivo).read_bytes())["models"]}

a, b = map(inventario, sys.argv[1:])
for modelo in ("gemma3:1b", "qwen2.5:1.5b-instruct-q4_K_M"):
    if a[modelo] != b.get(modelo):
        sys.exit(f"El digest de {modelo} difiere del Experimento A.")
PY
if [[ $# -eq 0 ]]; then
{
    git rev-parse HEAD
    uname -sr
    lscpu | grep -E '^(CPU\(s\)|Model name|Architecture):'
    free -mh
    ollama --version
    ollama ps
    node --version
    "$PROMPTFOO_PYTHON" --version
    "${cli[@]}" --version
    sha256sum "$cfg" prompts/criterios/{v3.txt,casos.yaml,esquema.json,aserciones.py,renderizar_iteraciones.py}
} > "$salida/entorno.txt"

codigo=0
LOG_LEVEL=debug "${cli[@]}" "${eval_args[@]}" --filter-pattern '^HU-01' -o "$salida/prueba.json" > "$salida/prueba-debug.log" 2>&1 || codigo=$?
printf '%s\n' "$codigo" > "$salida/codigo-prueba.txt"
test "$codigo" -eq 0 -o "$codigo" -eq 100
fi

PYTHONPATH=. "$PROMPTFOO_PYTHON" "$raiz/verificar_prueba_b.py" "$salida" > "$salida/prueba-http.json"
echo "Prueba corta verificada: dos POST con format=json, HTTP 200 y JSON literal."
codigo=0
"${cli[@]}" "${eval_args[@]}" -o "$salida/promptfoo.json" 2>&1 | tee "$salida/evaluacion.log" || codigo=$?
printf '%s\n' "$codigo" > "$salida/codigo-evaluacion.txt"
test "$codigo" -eq 0 -o "$codigo" -eq 100
PYTHONPATH=. "$PROMPTFOO_PYTHON" "$raiz/metricas.py" "$salida/promptfoo.json" > "$salida/metricas.json"
PYTHONPATH=. "$PROMPTFOO_PYTHON" "$raiz/auditar_respuestas.py" "$salida/promptfoo.json" > "$salida/auditoria.json"
