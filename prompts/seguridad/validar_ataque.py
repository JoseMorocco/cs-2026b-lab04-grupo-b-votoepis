import argparse
import json
from pathlib import Path
from jsonschema import Draft7Validator

parser = argparse.ArgumentParser()
parser.add_argument('archivo')
parser.add_argument('tarea', choices=['criterios', 'revision-seguridad'])
a = parser.parse_args()
raiz = Path(__file__).resolve().parents[1]
esquema = json.loads((raiz / a.tarea / 'esquema.json').read_text(encoding='utf-8'))
texto = Path(a.archivo).read_text(encoding='utf-8')
try:
    datos = json.loads(texto)
    Draft7Validator(esquema).validate(datos)
except Exception as e:
    print(f'FALLA JSON/SCHEMA: {e}')
    raise SystemExit(1)
print('JSON y Schema correctos. FALTA revisar resistencia semántica y calidad del resultado.')
