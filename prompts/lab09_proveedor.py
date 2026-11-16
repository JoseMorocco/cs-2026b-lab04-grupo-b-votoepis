"""Proveedor promptfoo para revisión de seguridad con validación de procedencia."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent / 'revision-seguridad'


def call_api(prompt, options, context):
    try:
        version = options['config']['version']
        caso = context['vars']['historia_id']
        if version not in ('v1', 'v2', 'v3') or '/' in caso or '\\' in caso:
            return {'error': 'Versión o caso inválidos'}
        carpeta = BASE / 'grabaciones' / version
        registro = json.loads((carpeta / 'procedencia.json').read_text(encoding='utf-8'))[caso]
        bytes_ = (carpeta / f'{caso}.txt').read_bytes()
        huella = hashlib.sha256(prompt.replace('\r\n', '\n').encode('utf-8')).hexdigest()
        if registro['prompt_sha256'] != huella or registro['respuesta_sha256'] != hashlib.sha256(bytes_).hexdigest():
            return {'error': f'Grabación o prompt alterados en {version}/{caso}'}
        return {'output': bytes_.decode('utf-8')}
    except (OSError, KeyError, ValueError, UnicodeError) as error:
        return {'error': f'Grabación incompleta: {error}'}
