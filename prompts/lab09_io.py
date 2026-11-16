"""Captura manual reproducible para los prompts de Lab09 (no genera respuestas)."""
import argparse
import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent


def preparar(tarea, version, caso_id):
    base = ROOT / tarea
    casos = yaml.safe_load((base / 'casos.yaml').read_text(encoding='utf-8'))
    vars_ = next(c['vars'] for c in casos if c['vars']['historia_id'] == caso_id)
    template = (base / f'{version}.txt').read_text(encoding='utf-8')
    # Conservar exactamente el salto final de la plantilla.
    prompt = template.replace('{{historia_id}}', vars_['historia_id']).replace('{{historia}}', vars_['historia'])
    return base, prompt


def digest(texto):
    return hashlib.sha256(texto.replace('\r\n', '\n').encode('utf-8')).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('accion', choices=['prompt', 'registrar', 'verificar'])
    ap.add_argument('tarea', choices=['criterios', 'revision-seguridad'])
    ap.add_argument('version', choices=['v1', 'v2', 'v3'])
    ap.add_argument('id', nargs='?')
    ap.add_argument('--archivo', type=Path)
    ap.add_argument('--asistente')
    ap.add_argument('--modelo', default='no verificado')
    args = ap.parse_args()
    base = ROOT / args.tarea
    casos = yaml.safe_load((base / 'casos.yaml').read_text(encoding='utf-8'))
    ids = [c['vars']['historia_id'] for c in casos]
    carpeta = base / 'grabaciones' / args.version
    manifiesto = carpeta / 'procedencia.json'
    if args.accion == 'verificar':
        from hashlib import sha256
        registros = json.loads(manifiesto.read_text(encoding='utf-8'))
        assert set(registros) == set(ids), f'Faltan o sobran casos: {set(ids) ^ set(registros)}'
        for id_ in ids:
            _, prompt = preparar(args.tarea, args.version, id_)
            bruto = (carpeta / f'{id_}.txt').read_bytes()
            assert registros[id_]['prompt_sha256'] == digest(prompt), id_
            assert registros[id_]['respuesta_sha256'] == sha256(bruto).hexdigest(), id_
        print(f'{len(ids)} respuestas verificadas: {args.tarea}/{args.version}')
        return
    assert args.id in ids, f'ID no encontrado. Opciones: {ids}'
    _, prompt = preparar(args.tarea, args.version, args.id)
    if args.accion == 'prompt':
        assert args.archivo, 'Indica --archivo'
        args.archivo.write_bytes(prompt.encode('utf-8'))
        print(f'Prompt completo: {args.archivo}')
        return
    assert args.archivo and args.asistente, 'Indica --archivo y --asistente'
    carpeta.mkdir(parents=True, exist_ok=True)
    registros = json.loads(manifiesto.read_text(encoding='utf-8')) if manifiesto.exists() else {}
    destino = carpeta / f'{args.id}.txt'
    assert args.id not in registros and not destino.exists(), 'Ya existe: no sobrescribas una captura'
    respuesta = args.archivo.read_bytes()
    assert respuesta.decode('utf-8').strip(), 'Respuesta vacía o inválida'
    destino.write_bytes(respuesta)
    registros[args.id] = {
        'asistente': args.asistente,
        'modelo_reportado': args.modelo,
        'prompt_sha256': digest(prompt),
        'respuesta_sha256': hashlib.sha256(respuesta).hexdigest(),
    }
    manifiesto.write_text(json.dumps(registros, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'Registrado: {destino}')


if __name__ == '__main__':
    main()
